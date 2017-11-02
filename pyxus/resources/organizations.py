from pyxus.resources.resource import Resource


class Organization(Resource):

    def create(self, name, description):
        api = '/organizations/{name}'.format(name=name)
        return self.http_client.put(api, self._create_json(name, description))

    def update(self, name, description, revision=None):
        if revision is None:
            revision = self.get_last_revision(name)
        api = '/organizations/{name}?rev={previous_rev}'.format(name=name, previous_rev=revision)
        return self.http_client.put(api, self._create_json(name, description))

    def get_last_revision(self, organization):
        return Resource.get_revision(self.read(organization))

    def read(self, name, revision=None):
        if revision is None:
            api = '/organizations/{name}'.format(name=name)
        else:
            api = '/organizations/{name}?rev={rev}'.format(name=name, rev=revision)
        return self.http_client.read(api)

    def list(self, name):
        api = '/organizations/{name}'.format(name=name)
        return self.http_client.read(api)

    @staticmethod
    def _create_json(name, description):
        obj = {
            "@context": {
                "schema": "http://schema.org/"
            },
            "schema:name": name,
            "schema:description": description
        }
        return obj