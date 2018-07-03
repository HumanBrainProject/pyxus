#   Copyright (c) 2018, EPFL/Human Brain Project PCO
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import logging
import re
import codecs

from abc import abstractmethod
from pyxus.resources.entity import Context, Domain, Entity, Instance, Organization, SearchResult, SearchResultList, Schema


if hasattr(str, "decode"):  # Python 2
    def decode_escapes(s):
        return s.decode("string_escape")
else:                       # Python 3
    def decode_escapes(s):
        return codecs.getdecoder('unicode_escape')(s)[0]


class Repository(object):

    def __init__(self, http_client, constructor):
        self.logger = logging.getLogger(__name__)
        self.path = constructor.path
        self._http_client = http_client
        self.constructor = constructor

    def create(self, entity):
        self.logger.debug("Creating entity: %s", entity)
        result = self._http_client.put(entity.path, entity.data)
        if result is not None:
            self.logger.info("%s created: %s", entity.__class__.__name__, entity.path)
        entity.data = result
        return entity

    def update(self, entity):
        self.logger.debug("Updating entity: %s", entity)
        revision = entity.get_revision()
        if revision is None:
            revision = self._get_last_revision(entity.id)
        path = "{}?rev={}".format(entity.path, revision)
        result = self._http_client.put(path, entity.data)
        if result is not None:
            new_revision = result["nxv:rev"]
            self.logger.info("%s updated: %s", entity.__class__.__name__, entity.path)
            entity.data = self._read(entity.id, new_revision)
        return entity

    def delete(self, entity, revision=None):
        self.logger.debug("Deleting entity: %s", entity)
        if revision is None:
            revision = self._get_last_revision(entity.id)
        if not entity.is_deprecated():
            path = "{}?rev={}".format(entity.path, revision)
            result = self._http_client.delete(path)
            if result is not None:
                self.logger.info("%s removed: %s", entity.__class__.__name__, entity.path)
                new_revision = result["nxv:rev"]
                entity.data = self._read(entity.id, new_revision)
        return entity

    def _read(self, identifier, revision=None):
        if revision is None:
            path = "{}/{}".format(self.path, identifier)
        else:
            path = "{}/{}?rev={}".format(self.path, identifier, revision)
        # try:
        return self._http_client.get(path)
        # except HTTPError as e:
        #     if e.response.status_code==401:
        #         return None
        #     raise e

    def _wrap_with_entity(self, search_result):
        identifier = Entity.extract_id_from_url(search_result.self_link, self.path)
        if isinstance(search_result.data, dict) and "source" in search_result.data:
            return self.constructor(identifier, search_result.data["source"], self.path)
        return None

    def list_by_full_subpath(self, subpath, resolved=False, deprecated=False):
        if not subpath.startswith('/'):
            subpath = u"/{}".format(subpath)
        if resolved:
            path = "{path}{subpath}&fields=all".format(path=self.path, subpath=subpath or '')
        else:
            path = "{path}{subpath}".format(path=self.path, subpath=subpath or '')
        return self.list_by_full_path(path, deprecated)

    def list_by_full_path(self, path, deprecated=False):
        path = decode_escapes(path)
        resolved = "fields=all" in path
        deprecated = "deprecated={}".format(deprecated) if deprecated is not None else ''
        path = "{path}&{deprecated}".format(path=path, deprecated=deprecated) if '?' in path else "{path}?{deprecated}".format(path=path, deprecated=deprecated)
        result = self._http_client.get(path)
        if result is not None:
            results = [SearchResult(r) for r in result["results"]]
            if resolved:
                results = [self._wrap_with_entity(r) for r in results]
            return SearchResultList(result["total"], results, result["links"])
        return None

    def list(self, resolved=False, subpath=None, full_text_query=None, filter_query=None, from_index=None, size=None, deprecated=False, context=None):
        subpath = "{subpath}/?{full_text_search_query}&{filter}&{context}&{from_index}&{size}&{deprecated}".format(
            subpath=subpath or '',
            full_text_search_query="q={}".format(full_text_query) if full_text_query is not None else '',
            filter="filter={}".format(filter_query) if filter_query is not None else '',
            context="context={}".format(context) if context is not None else '',
            from_index="from={}".format(from_index) if from_index is not None else '',
            size="size={}".format(size) if size is not None else '',
            deprecated="deprecated={}".format(deprecated) if deprecated is not None else ''
        )
        return self.list_by_full_subpath(subpath, resolved)

    def _get_last_revision(self, identifier):
        current_revision = self._read(identifier)
        if current_revision is not None and "nxv:rev" in current_revision:
            return current_revision.get("nxv:rev") or 0
        return 0

    def resolve_all(self, search_result_list):
        return [self.resolve(search_result) for search_result in search_result_list.results]

    def find_by_identifier(self, subpath, value, resolved=False, deprecated=False):
        return self.find_by_field(subpath, "http://schema.org/identifier", value, resolved=resolved, deprecated=deprecated)

    def find_by_field(self, subpath, field_path, value, resolved=False, deprecated=False):
        if not subpath.startswith('/'):
            subpath = u"/{}".format(subpath)
        path = "{path}{subpath}/?&filter={{\"op\":\"eq\",\"path\":\"{field_path}\",\"value\":{value}}}&{deprecated}".format(
            path=self.path,
            subpath=subpath,
            field_path=field_path,
            deprecated="deprecated={}".format(deprecated) if deprecated is not None else '',
            value=u"\"{}\"".format(value) if isinstance(value, (str, unicode)) else value
        )
        if resolved:
            path += "&fields=all"
        result = self._http_client.get(path)
        if result is not None:
            results = [SearchResult(r) for r in result["results"]]
            if resolved:
                results = [self._wrap_with_entity(r) for r in results]
            return SearchResultList(result["total"], results, result["links"])
        return None

    def fulltext_search(self, value, subpath=None, resolved=False, deprecated=False):
        if subpath is not None and not subpath.startswith('/'):
            subpath = u"/{}".format(subpath)
        else:
            subpath = ""
        path = "{path}{subpath}/?&q={query}&{deprecated}".format(
            path=self.path,
            subpath=subpath,
            query=value,
            deprecated="deprecated={}".format(deprecated) if deprecated is not None else ''
        )
        if resolved:
            path += "&fields=all"
        result = self._http_client.get(path)
        if result is not None:
            results = [SearchResult(r) for r in result["results"]]
            if resolved:
                results = [self._wrap_with_entity(r) for r in results]
            return SearchResultList(result["total"], results, result["links"])
        return None

    @abstractmethod
    def resolve(self, search_result):
        pass


class OrganizationRepository(Repository):

    def __init__(self, http_client):
        super(OrganizationRepository, self).__init__(http_client, Organization)

    def read(self, name, revision=None):
        data = self._read(name, revision)
        return Organization(name, data, self.path) if data is not None else None

    def resolve(self, search_result):
        identifier = Entity.extract_id_from_url(search_result.self_link, self.path)
        data = self._read(identifier)
        return Organization(identifier, data, self.path) if data is not None else None


class DomainRepository(Repository):

    def __init__(self, http_client):
        super(DomainRepository, self).__init__(http_client, Domain)

    def read(self, organization, domain, revision=None):
        identifier = Domain.create_id(organization, domain)
        data = self._read(identifier, revision)
        return Domain(identifier, data, self.path) if data is not None else None

    def resolve(self, search_result):
        identifier = Entity.extract_id_from_url(search_result.self_link, self.path)
        data = self._read(identifier)
        return Domain(identifier, data, self.path) if data is not None else None


class SchemaRepository(Repository):

    def __init__(self, http_client):
        super(SchemaRepository, self).__init__(http_client, Schema)

    def read(self, organization, domain, schema, version, revision=None):
        identifier = Schema.create_id(organization, domain, schema, version)
        data = self._read(identifier, revision)
        return Schema(identifier, data, self.path) if data is not None else None

    def publish(self, entity, publish, revision=None):
        if revision is None:
            revision = self._get_last_revision(entity.id)
        path = "{}/config?rev={}".format(entity.path, revision)
        result = self._http_client.patch(path, {
            'published': publish
        })
        if result is not None:
            new_revision = result["nxv:rev"]
            entity.data = self._read(entity.id, new_revision)
        return entity

    def resolve(self, search_result):
        identifier = Entity.extract_id_from_url(search_result.self_link, self.path)
        data = self._read(identifier)
        return Schema(identifier, data, self.path) if data is not None else None


class InstanceRepository(Repository):

    def __init__(self, http_client):
        super(InstanceRepository, self).__init__(http_client, Instance)

    def create(self, entity):
        result = self._http_client.post(entity.path, entity.data)
        if result is None:
            raise ValueError("Entity was not created")
        else:
            self.logger.info("Instance created: %s", entity.path)
        entity.data = result
        entity.id = Instance.extract_id_from_url(result.get("@id"), self.path)
        entity.build_path()
        return entity

    @staticmethod
    def _extract_uuid(full_id_string):
        regex = "[^/]*$"
        r = re.search(regex, full_id_string)
        if r is not None:
            return r.group(0)
        return None

    def read_by_full_id(self, full_id, revision=None):
        data = self._read(full_id, revision)
        return Instance(full_id, data, self.path) if data is not None else None

    def read(self, organization, domain, schema, version, uuid, revision=None):
        identifier = Instance.create_id(organization, domain, schema, version) + "/" + uuid
        data = self._read(identifier, revision)
        return Instance(identifier, data, self.path) if data is not None else None

    def resolve(self, search_result):
        identifier = Entity.extract_id_from_url(search_result.self_link, self.path)
        data = self._read(identifier)
        return Instance(identifier, data, self.path) if data is not None else None

    def list_by_schema(self, organization, domain, schema, version, resolved=False, full_text_query=None, filter_query=None,
                       from_index=None, size=None, deprecated=False):
        return self.list(subpath="/{}/{}/{}/{}".format(organization, domain, schema, version),
                         resolved=resolved, full_text_query=full_text_query, filter_query=filter_query,
                         from_index=from_index, size=size, deprecated=deprecated)


class ContextRepository(Repository):

    def __init__(self, http_client):
        super(ContextRepository, self).__init__(http_client, Context)

    def read(self, organization, domain, context, version, revision=None):
        identifier = Context.create_id(organization, domain, context, version)
        data = self._read(identifier, revision)
        return Context(identifier, data, self.path) if data is not None else None

    def publish(self, entity, publish, revision=None):
        if revision is None:
            revision = self._get_last_revision(entity.id)
        path = "{}/config?rev={}".format(entity.path, revision)
        result = self._http_client.patch(path, {
            'published': publish
        })
        if result is not None:
            new_revision = result["nxv:rev"]
            entity.data = self._read(entity.id, new_revision)
        return entity

    def resolve(self, search_result):
        identifier = Entity.extract_id_from_url(search_result.self_link, self.path)
        data = self._read(identifier)
        return Context(identifier, data, self.path) if data is not None else None
