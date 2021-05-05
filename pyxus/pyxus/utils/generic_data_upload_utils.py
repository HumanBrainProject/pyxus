#  Copyright 2018 - 2021 Swiss Federal Institute of Technology Lausanne (EPFL)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0.
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  This open source software code was developed in part or in whole in the
#  Human Brain Project, funded from the European Union's Horizon 2020
#  Framework Programme for Research and Innovation under
#  Specific Grant Agreements No. 720270, No. 785907, and No. 945539
#  (Human Brain Project SGA1, SGA2 and SGA3).
#


import json
import logging
import re

import pystache
from requests.exceptions import HTTPError

from pyxus.client import NexusException
from pyxus.resources.entity import Organization, Domain, Instance, Schema, Context, Entity

class ResolveByIdentifierError(Exception):
    def __init__(self, message, path):
        super(ResolveByIdentifierError, self).__init__(message)
        self.path=path

class GenericDataUploadUtils(object):
    _client = None

    def __init__(self, nexus_client, upload_fully_qualified=True):
        self.logger = logging.getLogger(__name__)
        self._client = nexus_client
        self._upload_fully_qualified = upload_fully_qualified
        self._id_cache = {}

    def create_instance(self, data, schema_data, fail_if_linked_instance_is_missing=True):
        """Create a new instance for the provided data

        Arguments:
            file_path -- path to the location of the file to be uploaded as instance
            fully_qualify -- if True, prefixes are resolved and the JSON-LD to be uploaded will be interpretable as JSON
                             (but with non-human-friendly, fully qualified keys)
        """
        raw_json = self.resolve_entities(data if not isinstance(data, dict) else json.dumps(data), fail_if_linked_instance_is_missing)
        raw_json = self._fill_placeholders(raw_json)
        fully_qualified_json = Entity.fully_qualify(json.loads(raw_json))
        if not self._upload_fully_qualified:
            final_json = json.loads(raw_json) if not isinstance(raw_json, dict) else raw_json
        else:
            final_json = fully_qualified_json
        schema_identifier = "http://schema.org/identifier"
        hashcode_field = "http://hbp.eu/internal#hashcode"
        if self._upload_fully_qualified:
            raw_json = final_json
        instance = Instance.create_new(schema_data.organization, schema_data.domain, schema_data.name, schema_data.version, raw_json)
        if hashcode_field not in fully_qualified_json:
            current_hashcode = Entity.do_get_checksum(fully_qualified_json)
            fully_qualified_json[hashcode_field] = current_hashcode
            instance.data[hashcode_field] = current_hashcode
        else:
            current_hashcode = fully_qualified_json[hashcode_field]
        if schema_identifier in fully_qualified_json:
            identifier = fully_qualified_json.get(schema_identifier)
            result = self.handle_known_schema_identifier(schema_identifier, instance, hashcode_field, current_hashcode, identifier)
            if result is not None:
                return result
        return self._client.instances.create(Instance.create_new(schema_data.organization, schema_data.domain, schema_data.name, schema_data.version, raw_json))

    def handle_known_schema_identifier(self, schema_identifier, instance, hashcode_field, current_hashcode, identifier):
        if isinstance(identifier, list):
            identifier = identifier[0]
        found_instances = self._client.instances.find_by_field(instance.id, schema_identifier, identifier, resolved=True)
        if found_instances and found_instances.results:
            found_instance = found_instances.results[0]
            existing_hashcode = found_instance.data[hashcode_field] if hashcode_field in found_instance.data else None
            instance.path = found_instance.get_self_link()
            instance.id = Instance.extract_id_from_url(instance.path, instance.root_path)
            if existing_hashcode is None or existing_hashcode != current_hashcode:
                result = self._client.instances.update(instance)
            else:
                self.logger.debug("Skipping instance %s because it already exists", instance.path)
                result = instance
            return result
        return None

    def _fill_placeholders(self, template):
        template = template.replace("{{endpoint}}:{{port}}/{{prefix}}", "{{base}}")
        # in our structure, the port is already included within the host string -
        # to make sure we don't have any broken namespaces, we have to remove it from the template
        template = template.replace(":{{port}}", "")
        return pystache.render(template, base="{}/{}".format(
            self._client.config.NEXUS_NAMESPACE,
            self._client.config.NEXUS_PREFIX), prefix=self._client.config.NEXUS_PREFIX)

    def resolve_identifier(self, match):
        if match in self._id_cache:
            self.logger.debug("resolved %s from cache", match)
            return self._id_cache.get(match)
        else:
            result_list = self._client.instances.list_by_full_subpath(match + "&deprecated=false")
            if result_list is not None and result_list.results:
                # TODO check - do we really want to select the first one if ambiguous?
                result = result_list.results[0].result_id
                self._id_cache[match] = result
                return result
            else:
                raise ResolveByIdentifierError("No entities found for {}".format(match), match)

    def resolve_entities(self, template, fail_if_linked_instance_is_missing):
        search_pattern = r"(?<=\"\{\{resolve_by_identifier) (?P<path>.*?) (?P<identifier>.*?)(?=\}\}\")"
        replace_pattern = "\"{{{{resolve_by_identifier {} {}}}}}\""
        matches = re.findall(search_pattern, template)
        for match in matches:
            path = match[0].strip("/")
            identifier = match[1].strip("/")
            replace = replace_pattern.format(match[0], match[1])
            filter_condition = "?filter=" + json.dumps({"op": "eq", "path": "http://schema.org/identifier", "value": identifier}).replace('"', '\\"')
            template = template.replace(replace, "\"{{{{resolve /{}{}}}}}\"".format(path, filter_condition))

        matches = re.findall(r"(?<=\{\{resolve ).*?\}(?=\}\})", template)
        for match in matches:
            try:
                replacement = self.resolve_identifier(match)
            except ResolveByIdentifierError as e:
                if not fail_if_linked_instance_is_missing:
                    replacement = ""
                else:
                    raise e
            template = template.replace("\"{{resolve " + match + "}}\"", "{{ \"@id\": \"{}\"}}".format(replacement if replacement is not None else ""))
        matches = re.findall(r"(?<=\{\{resolve_id ).*?\}(?=\}\})", template)
        for match in matches:
            try:
                replacement = self.resolve_identifier(match)
            except ResolveByIdentifierError as e:
                if not fail_if_linked_instance_is_missing:
                    replacement=""
                else:
                    raise e
            template = template.replace("{{resolve_id " + match + "}}", replacement if replacement is not None else "")
        return template

    def clear_all_instances(self, subpath=None):
        all_instances = self._client.instances.list(subpath, size=999999)
        all_instances = self._client.instances.resolve_all(all_instances)
        for instance in all_instances:
            self._client.instances.delete(instance)

    def create_schema(self, data, force_domain_creation=False, update_if_already_exists=False, publish=False):
        entity = Schema.create_new(data.organization, data.domain, data.name, data.version, data.content)
        return self._create_schema_or_context("schema", self._client.schemas, entity, data, force_domain_creation,
                                              update_if_already_exists, publish)

    def create_context(self, data, force_domain_creation=False, update_if_already_exists=False, publish=False):
        entity = Context.create_new(data.organization, data.domain, data.name, data.version, data.content)
        return self._create_schema_or_context("context", self._client.contexts, entity, data, force_domain_creation,
                                              update_if_already_exists, publish)

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
            schema_or_context = self._client.schemas.update(data.organization, data.domain, data.name, data.version,
                                                            data.content, schema_or_context.get_revision())
        data.revision = schema_or_context.get_revision()
        if publish and data.revision and not schema_or_context.is_published():
            repository.publish(schema_or_context, True, data.revision)
        return data

    @staticmethod
    def _process_content(content):
        return content
