from pyxus.resources.resource import Resource


class Domain(Resource):

    def create(self, organization, domain, description):
        api = '/organizations/{org}/domains/{dom}'.format(
            org=organization,
            dom=domain
        )
        return self.http_client.put(api, self._create_json(description))

    def update(self, organization, domain, description, revision=None):
        if revision is None:
            revision = self.get_last_revision(organization, domain)
        api = '/organizations/{org}/domains/{dom}?rev={rev}'.format(
            org=organization,
            dom=domain,
            rev=revision
        )
        return self.http_client.put(api, self._create_json(description))

    def read(self, organization, domain, revision=None):
        if revision is None:
            api = '/organizations/{org}/domains/{dom}'.format(
                org=organization,
                dom=domain
            )
        else:
            api = '/organizations/{org}/domains/{dom}?rev={rev}'.format(
                org=organization,
                dom=domain,
                rev=revision
            )
        return self.http_client.read(api)

    def deprecate(self, organization, domain, revision=None):
        if revision is None:
            revision = self.get_last_revision(organization, domain)
        api = '/organizations/{org}/domains/{dom}?rev={rev}'.format(
            org=organization,
            dom=domain,
            rev=revision
        )
        return self.http_client.delete(api)

    def get_last_revision(self, organization, domain):
        return Resource.get_revision(self.read(organization, domain))

    @staticmethod
    def _create_json(description):
        obj = {
            'description': description
        }
        return obj