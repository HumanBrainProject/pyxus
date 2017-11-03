import re


class Entity(object):

    def __init__(self, identifier, json, root_path):
        self.id = identifier
        self.json = json
        self.root_path = root_path
        self.path = None
        self.build_path()

    def build_path(self):
        self.path = "{}/{}".format(self.root_path, self.id)

    def get_revision(self):
        return self.json["rev"]

    def __str__(self):
        return "{classname}: id={id}, path={path}, revision={revision}\ndata={data}".format(
            classname=self.__class__.__name__,
            id=self.id,
            path=self.path,
            revision=self.get_revision(),
            data=self.json
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
        return self.json["published"] if "published" in self.json else False


class Instance(Entity):
    path = "/data"

    @staticmethod
    def create_id(organization, domain, schema, version):
        return "{}/{}/{}/{}".format(organization, domain, schema, version)

    @classmethod
    def create_new(cls, organization, domain, schema, version, content):
        identifier = Instance.create_id(organization, domain, schema, version)
        return Instance(identifier, content, Instance.path)


class SearchResultList(object):

    def __init__(self, total, results):
        self.total = total
        self.results = results

    def __str__(self):
        return "{classname}: total={total}, first_entry=({first_entry})".format(
            classname=self.__class__.__name__,
            total=self.total,
            first_entry=self.results[0] if self.results is not None and len(self.results) > 0 else "no results"
        )


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
