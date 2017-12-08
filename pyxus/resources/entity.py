import hashlib
import json
import re
from pyld import jsonld

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

    def get_checksum(self):
        return hashlib.md5(json.dumps(self.data).encode("utf-8")).hexdigest()

    def get_simplified_data(self):
        return self._get_simplified_data(self.data)

    def get_data(self, key, simplified=True):
        if key in self.data:
            return self._get_simplified_data(self.data[key]) if simplified else self.data[key]
        elif simplified:
            for k in self.data:
                if re.match(".*?:"+key, k):
                    return  self._get_simplified_data(self.data[k])
        return None

    @staticmethod
    def _get_simplified_data(data):
        if not type(data) is dict:
            return data
        simple = {}
        for key in data:
            if not key.startswith("@"):
                new_key = re.sub(".*?:", "", key)
                if type(data[key]) is dict:
                    simple[new_key] = Entity._get_simplified_data(data[key])
                else:
                    simple[new_key] = data[key]
        return simple

    def get_revision(self):
        return self.data["rev"] if "rev" in self.data else None

    def __str__(self):
        return "{classname}: id={id}, path={path}, revision={revision}\ndata={data}".format(
            classname=self.__class__.__name__,
            id=self.id,
            path=self.path,
            revision=self.get_revision(),
            data=self.data
        )

    @staticmethod
    def extract_id_from_url(url, root_path):
        regex = "(?<={root_path}/).*?(?=(\?|$|#))".format(root_path=root_path)
        r = re.search(regex, url)
        if r is not None:
            result = r.group(0)
            if result.endswith('/'):
                return result[:-1]
            return result
        raise ValueError("\"{url}\" is not applicable to {root_path}!".format(url=url, root_path=root_path))

    def is_deprecated(self):
        return self.data.get("deprecated")!=False


    def get_identifier(self):
        if "http://schema.org/identifier" in self.data:
            return self.data.get("http://schema.org/identifier")
        return None

class Organization(Entity):

    path = "/organizations"

    @classmethod
    def create_new(cls, name, description):
        json = {
            "@context": {
                "schema2": "http://schema.org/"
            },
            "schema:name": name,
            "schema:description": description
        }
        return Organization(name, json, Organization.path)


class Domain(Entity):
    path = "/domains"

    @staticmethod
    def create_id(organization, domain):
        return "{}/{}".format(organization, domain)

    @classmethod
    def create_new(cls, organization, domain, description):
        json = {
            'description': description
        }
        identifier = Domain.create_id(organization, domain)
        return Domain(identifier, json, Domain.path)


class Schema(Entity):
    path = "/schemas"

    @staticmethod
    def create_id(organization, domain, schema, version):
        return "{}/{}/{}/{}".format(organization, domain, schema, version)

    @classmethod
    def create_new(cls, organization, domain, schema, version, content):
        identifier = Schema.create_id(organization, domain, schema, version)
        return Schema(identifier, content, Schema.path)

    def is_published(self):
        return self.data["published"] if "published" in self.data else False


class Instance(Entity):
    path = "/data"

    @staticmethod
    def create_id(organization, domain, schema, version):
        return "{}/{}/{}/{}".format(organization, domain, schema, version)

    @classmethod
    def create_new(cls, organization, domain, schema, version, content):
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
        return self.data["published"] if "published" in self.data else False


class SearchResultList(object):

    def __init__(self, total, results, links):
        self.total = total
        self.results = results
        self.links = links

    def __str__(self):
        return "{classname}: total={total}, first_entry=({first_entry})".format(
            classname=self.__class__.__name__,
            total=self.total,
            first_entry=self.results[0] if self.results is not None and len(self.results) > 0 else "no results"
        )

    def get_next_link(self):
        for link in self.links:
            if "rel" in link and link.get("rel")=="next":
                return link["href"]
        return None


    def get_previous_link(self):
        for link in self.links:
            if "rel" in link and link.get("rel") == "previous":
                return link["href"]
        return None


class SearchResult(object):
    result_id = None
    self_link = None
    data = None

    def __init__(self, result_dict):
        self.data = result_dict
        self.result_id = result_dict['resultId']
        links = result_dict['source']['links']
        self.self_link = str([x['href'] for x in links if x['rel'] == 'self'][0])

    def __str__(self):
        return 'result_id:{}, link:{}, data:{}'.format(self.result_id, self.self_link, self.data)
