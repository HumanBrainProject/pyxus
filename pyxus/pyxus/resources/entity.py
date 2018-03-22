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


import hashlib
import json
import re
from pyld import jsonld

from pyxus.utils.turtle_schema_transformer import transform_turtle_to_jsonld_schema, transform_turtle_to_jsonld


class Entity(object):

    def __init__(self, identifier, data, root_path):
        self.id = identifier
        self.data = data
        self.root_path = root_path
        self.path = None
        self.build_path()

    def build_path(self):
        self.path = "{}/{}".format(self.root_path, self.id)

    @staticmethod
    def fully_qualify(data):
        data = jsonld.expand(data)
        data = jsonld.compact(data, {})
        return data

    def to_json(self):
        return json.dumps(self.data, indent=4)

    def get_checksum(self):
        return hashlib.md5(json.dumps(self.data).encode("utf-8")).hexdigest()

    def get_simplified_data(self):
        return self._get_simplified_data(self.data)

    def get_data(self, key, simplified=True):
        if key in self.data:
            return self._get_simplified_data(self.data[key]) if simplified else self.data[key]
        elif simplified:
            for k in self.data:
                if re.match(".*?:" + key, k):
                    return self._get_simplified_data(self.data[k])
        return None

    @staticmethod
    def _get_simplified_data(data):
        if not isinstance(data, dict):
            return data
        simple = {}
        for key in data:
            if not key.startswith("@"):
                new_key = re.sub(".*?:", "", key)
                if isinstance(data[key], dict):
                    simple[new_key] = Entity._get_simplified_data(data[key])
                else:
                    simple[new_key] = data[key]
        return simple

    def get_revision(self):
        return self.data["nxv:rev"] if "nxv:rev" in self.data else None

    def __str__(self):
        return "{classname}: id={id}, path={path}, revision={revision}\ndata={data}".format(
            classname=self.__class__.__name__,
            id=self.id,
            path=self.path,
            revision=self.get_revision(),
            data=self.data
        )

    extract_info = r"(?P<org>.*)/(?P<domain>.*)/(?P<schema>.*)/(?P<version>.*)/(?P<id>.*)"

    def get_type(self):
        return self.data["@type"]

    def get_organization(self):
        return re.match(r"(?P<org>.*?)(/.*)?$", self.id).group("org")

    def get_domain(self):
        return re.match(r".*?/(?P<domain>.*?)(/.*)?$", self.id).group("domain")

    def get_schema(self):
        return re.match(r".*?/.*?/(?P<schema>.*?)(/.*)?$", self.id).group("schema")

    def get_version(self):
        return re.match(r".*?/.*?/.*?/(?P<version>.*?)(/.*)?$", self.id).group("version")

    def get_id(self):
        return Entity.get_uuid_from_id(self.id)

    @staticmethod
    def get_uuid_from_id(identifier):
        return re.match(r".*?/.*?/.*?/.*?/(?P<id>.*?)(/.*)?$", identifier).group("id")

    @staticmethod
    def extract_id_from_url(url, root_path):
        regex = r"(?<={root_path}/).*?(?=(\?|$|#))".format(root_path=root_path)
        r = re.search(regex, url)
        if r is not None:
            result = r.group(0)
            if result.endswith('/'):
                return result[:-1]
            return result
        raise ValueError("\"{url}\" is not applicable to {root_path}!".format(url=url, root_path=root_path))

    def is_deprecated(self):
        return self.data.get("nxv:deprecated") != False

    def get_identifier(self):
        if "http://schema.org/identifier" in self.data:
            return self.data.get("http://schema.org/identifier")
        return None


class Organization(Entity):
    path = "/organizations"

    @classmethod
    def create_new(cls, name, description):
        data = {
            "@context": {
                "schema2": "http://schema.org/"
            },
            "schema:name": name,
            "schema:description": description
        }
        return Organization(name, data, Organization.path)


class Domain(Entity):
    path = "/domains"

    @staticmethod
    def create_id(organization, domain):
        return "{}/{}".format(organization, domain)

    @classmethod
    def create_new(cls, organization, domain, description):
        data = {
            'description': description
        }
        identifier = Domain.create_id(organization, domain)
        return Domain(identifier, data, Domain.path)


class Schema(Entity):
    path = "/schemas"

    @staticmethod
    def create_id(organization, domain, schema, version):
        return "{}/{}/{}/{}".format(organization, domain, schema, version)

    @classmethod
    def create_new(cls, organization, domain, schema, version, content, is_turtle=False):
        if is_turtle:
            content = transform_turtle_to_jsonld_schema(content)
        identifier = Schema.create_id(organization, domain, schema, version)
        return Schema(identifier, content, Schema.path)

    def is_published(self):
        return self.data["nxv:published"] if "nxv:published" in self.data else False


class Instance(Entity):
    path = "/data"

    @staticmethod
    def create_id(organization, domain, schema, version):
        return "{}/{}/{}/{}".format(organization, domain, schema, version)

    @classmethod
    def create_new(cls, organization, domain, schema, version, content, is_turtle=False):
        if is_turtle:
            content = transform_turtle_to_jsonld(content)
            if isinstance(content, list) and len(content) == 1:
                content = content[0]
            else:
                raise ValueError("Can't handle multiple instances in same file!")
        identifier = Instance.create_id(organization, domain, schema, version)
        return Instance(identifier, content, Instance.path)


class Context(Entity):
    path = "/contexts"

    @staticmethod
    def create_id(organization, domain, context, version):
        return "{}/{}/{}/{}".format(organization, domain, context, version)

    @classmethod
    def create_new(cls, organization, domain, context, version, content):
        identifier = Context.create_id(organization, domain, context, version)
        return Context(identifier, content, Context.path)

    def is_published(self):
        return self.data["nxv:published"] if "nxv:published" in self.data else False


class SearchResultList(object):

    def __init__(self, total, results, links):
        self.total = total
        self.results = results
        self.links = links

    def __str__(self):
        return "{classname}: total={total}, first_entry=({first_entry})".format(
            classname=self.__class__.__name__,
            total=self.total,
            first_entry=self.results[0] if self.results is not None and self.results else "no results"
        )

    def get_next_link(self):
        return self.links["next"] if "next" in self.links else None

    def get_previous_link(self):
        return self.links["previous"] if "previous" in self.links else None


class SearchResult(object):
    result_id = None
    self_link = None
    data = None

    def __init__(self, result_dict):
        self.data = result_dict
        self.result_id = result_dict['resultId']
        self.self_link = result_dict['source']['links']['self']

    def __str__(self):
        return 'result_id:{}, link:{}, data:{}'.format(self.result_id, self.self_link, self.data)
