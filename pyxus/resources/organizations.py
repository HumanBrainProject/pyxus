class Organization(object):

    def __init__(self, http_client):
        self.http_client = http_client

    def create(self, name, desc):
        obj = {
            "@context": {
                "schema": "http://schema.org/"
            },
            "schema:name": name,
            "schema:description": desc
        }
        api = '/organizations/{name}'.format(name=name)
        return self.http_client.put(api, obj)

    def read(self, name):
        api = '/organizations/{name}'.format(name=name)
        return self.http_client.get(api)

    def list(self, name):
        api = '/organizations/{name}'.format(name=name)
        return self.http_client.get(api)
