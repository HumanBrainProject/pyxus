class Domain(object):

    def __init__(self, http_client):
        self.http_client = http_client

    def create(self, org, dom, desc):
        obj = {
            'description': desc
        }
        api = '/organizations/{org}/domains/{dom}'.format(
            org=org,
            dom=dom
        )
        return self.http_client.put(api, obj)

    def read(self, org, dom):
        api = '/organizations/{org}/domains/{dom}'.format(
            org=org,
            dom=dom
        )
        return self.http_client.get(api)
