import fnmatch
import json
import logging
import os
import os.path
import re

import pystache
from requests.exceptions import HTTPError

from pyxus.client import NexusException
from pyxus.resources.entity import Organization, Domain, Instance, Schema, Context, Entity
from pyxus.utils.schema_or_context_data import SchemaOrContextData

LOGGER = logging.getLogger(__package__)


def recursive_find_matching(root_path, pattern):
    matches = []
    for root, dirnames, filenames in os.walk(root_path):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))

    return matches


class DataUploadUtils(object):
    _client = None

    def __init__(self,  nexus_client, upload_fully_qualified=True):
        self._client = nexus_client
        self._upload_fully_qualified = upload_fully_qualified
        self._id_cache = {}

    def create_schema_by_file(self, file_path, force_domain_creation=False, update_if_already_exists=False, publish=False):
        return self.__create_schema_or_context_by_file(self._create_schema, file_path, force_domain_creation, update_if_already_exists, publish)

    def create_context_by_file(self, file_path, force_domain_creation=False, update_if_already_exists=False, publish=False):
        return self.__create_schema_or_context_by_file(self._create_context, file_path, force_domain_creation, update_if_already_exists, publish)

    def __create_schema_or_context_by_file(self, creation_function, file_path, force_domain_creation=False, update_if_already_exists=False, publish=False):
        """Create a new schema or context or revise an existing.

        Arguments:
        creation_function -- the function to create the structure (either for context or schema)
        file_path -- path to the location of the schema/context
        force_domain_creation -- if the organization and domain declared as part of the schema/context shall be created automatically
        update_if_already_exists -- if an already existing schema/context shall be updated.
        publish -- if the created or updated schema/context shall be published immediately (required for instance generation)
        """
        with open(file_path) as x:
            file_content = x.read()
            file_content = self._process_content(file_content)
            raw_content = self.__fill_placeholders(file_content)
            content = json.loads(raw_content)
            schema_data = SchemaOrContextData.by_filepath(file_path, content)
            return creation_function(schema_data, force_domain_creation, update_if_already_exists, publish)

    def create_instance_by_file(self, file_path, fully_qualify=False):
        """Create a new instance for the provided data

        Arguments:
            file_path -- path to the location of the file to be uploaded as instance
            fully_qualify -- if True, prefixes are resolved and the JSON-LD to be uploaded will be interpretable as JSON (but with non-human-friendly, fully qualified keys)
        """
        with open(os.path.abspath(file_path)) as metadata_file:
            file_content = metadata_file.read()
            raw_json = self.__resolve_entities(file_content)
            raw_json = self.__fill_placeholders(raw_json)
            if fully_qualify:
                final_json = Entity.fully_qualify(json.loads(raw_json))
            else:
                final_json = json.loads(raw_json) if type(raw_json) is not dict else raw_json
            schema_data = SchemaOrContextData.by_filepath(file_path, final_json)
            schema_identifier = "http://schema.org/identifier"
            if self._upload_fully_qualified:
                raw_json = final_json
            instance = Instance.create_new(schema_data.organization, schema_data.domain, schema_data.name, schema_data.version, raw_json)
            if schema_identifier in final_json:
                checksum = instance.get_checksum()
                checksum_file = "{}.{}.chksum".format(file_path, checksum)
                if os.path.exists(checksum_file):
                    LOGGER.debug("{} is unchanged - no upload required".format(file_path))
                    return
                identifier=final_json.get(schema_identifier)
                if type(identifier) is list:
                    identifier = identifier[0]
                found_instances = self._client.instances.find_by_field(instance.id, schema_identifier, identifier)
                if found_instances and len(found_instances.results)>0:
                    instance.path = found_instances.results[0].self_link
                    instance.id = Instance.extract_id_from_url(instance.path, instance.root_path)
                    result = self._client.instances.update(instance)
                    with open(checksum_file, 'a') as checksum_file:
                        checksum_file.close()
                    return result
            return self._client.instances.create(Instance.create_new(schema_data.organization, schema_data.domain, schema_data.name, schema_data.version, raw_json))

    def __fill_placeholders(self, template):
        template = template.replace("{{base}}", "{{endpoint}}:{{port}}/{{prefix}}")
        # in our structure, the port is already included within the host string -
        # to make sure we don't have any broken namespaces, we have to remove it from the template
        template = template.replace(":{{port}}", "")
        return pystache.render(template, endpoint=self._client.config.NEXUS_ENDPOINT, prefix=self._client.config.NEXUS_PREFIX)


    def __resolve_identifier(self, match):
        if match in self._id_cache:
            LOGGER.debug("resolved {} from cache".format(match))
            return self._id_cache.get(match)
        else:
            result_list = self._client.instances.list_by_full_subpath(match + "&deprecated=false")
            if result_list is not None and len(result_list.results) > 0:
                # TODO check - do we really want to select the first one if ambiguous?
                result = result_list.results[0].result_id
                self._id_cache[match] = result
                return result
            else:
                raise ValueError("No entities found for " + match)

    def __resolve_entities(self, template):
        matches = re.findall("(?<=\{\{resolve ).*(?=\}\})", template)
        for match in matches:
            template = template.replace("\"{{resolve "+match+"}}\"", "{{ \"@id\": \"{}\"}}".format(self.__resolve_identifier(match)))
        matches = re.findall("(?<=\{\{resolve_id ).*(?=\}\})", template)
        for match in matches:
            template = template.replace("{{resolve_id " + match + "}}", self.__resolve_identifier(match))
        return template

    def clear_all_checksums(self, path):
        for match in recursive_find_matching(path, "*.chksum"):
            os.remove(match)

    def clear_all_instances(self, subpath=None):
        all_instances = self._client.instances.list(subpath, size=999999)
        all_instances = self._client.instances.resolve_all(all_instances)
        for instance in all_instances:
            self._client.instances.delete(instance)

    def _create_schema(self, data, force_domain_creation, update_if_already_exists, publish):
        entity = Schema.create_new(data.organization, data.domain, data.name, data.version, data.content)
        return self._create_schema_or_context("schema", self._client.schemas, entity, data, force_domain_creation, update_if_already_exists, publish)

    def _create_context(self, data, force_domain_creation, update_if_already_exists, publish):
        entity = Context.create_new(data.organization, data.domain, data.name, data.version, data.content)
        return self._create_schema_or_context("context", self._client.contexts, entity, data, force_domain_creation, update_if_already_exists, publish)

    def _create_schema_or_context(self, text, repository, entity, data, force_domain_creation, update_if_already_exists, publish):
        try:
            schema_or_context = repository.read(data.organization, data.domain, data.name, data.version)
        except HTTPError as e:
            raise NexusException("Request for {} has failed: {}".format(text, e.message))

        if schema_or_context is None:
            # The schema or context does not exist yet - we create it
            if force_domain_creation:
                organization = self._client.organizations.read(data.organization)
                if organization is None:
                    self._client.organizations.create(Organization.create_new(data.organization, "Created by {} {}".format(text, data.name)))
                domain = self._client.domains.read(data.organization, data.domain)
                if domain is None:
                    self._client.domains.create(Domain.create_new(data.organization, data.domain, "Created by {} {}".format(text, data.name)))
            schema_or_context = repository.create(entity)
        elif update_if_already_exists:
            if schema_or_context.is_published():
                raise NexusException("Can not update the already published {} {}".format(text, data.name))
            schema_or_context = self._client.schemas.update(data.organization, data.domain, data.name, data.version, data.content, schema_or_context.get_revision())
        data.revision = schema_or_context.get_revision()
        if publish and data.revision and not schema_or_context.is_published():
            repository.publish(schema_or_context, True, data.revision)
        return data

    def _process_content(self, content):
        return content