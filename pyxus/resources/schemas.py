import logging
import json
from requests.exceptions import HTTPError

from pyxus.resources.resource import Resource
from pyxus.utils.exception import NexusException

logger = logging.getLogger(__name__)

class Schema(Resource):

    def create(self, organization, domain, schema, version, content):
        schema_path = Schema._build_schema_path(organization, domain, schema, version)
        api = '/schemas/{schema_path}'.format(schema_path=schema_path)
        logger.info("creating schema %s", api)
        return self.http_client.put(api, content)

    def create_with_domain(self, organization_repo, domain_repo, organization, domain, schema, version, content):
        organization_from_graph = organization_repo.read(organization)
        if organization_from_graph is None:
            logger.info("Creation of organization %s triggered by schema definition", organization)
            organization_repo.create(organization, "Organization created by schema {}. TODO: create better description".format(schema))

        domain = domain_repo.read_by_path(organization, domain)
        if domain is None:
            logger.info("Creation of domain %s in organization %s triggered by schema definition", organization, domain)
            domain_repo.create(organization, domain, "Domain created by schema {}. TODO: create better description".format(schema))

        return self.create(organization, domain, schema, version, content)

    def read(self, organization, domain, schema, version, revision=None):
        schema_path = Schema._build_schema_path(organization, domain, schema, version)
        if revision is None:
            api = '/schemas/{schema_path}'.format(schema_path=schema_path)
        else:
            api = '/schemas/{schema_path}?rev={rev}'.format(schema_path=schema_path, rev=revision)
        return self.http_client.read(api)

    def update(self, organization, domain, schema, version, content, previous_rev):
        schema_path = Schema._build_schema_path(organization, domain, schema, version)
        api = '/schemas/{schema_path}?rev={previous_rev}'.format(schema_path=schema_path, previous_rev=previous_rev)
        logger.info("updating schema %s", api)
        return self.http_client.put(api, content)

    def publish(self, organization, domain, schema, version, revision=None, publish=True):
        schema_path = Schema._build_schema_path(organization, domain, schema, version)
        if revision is None:
            revision = self.get_last_revision(schema_path)
        api = '/schemas/{schema_path}/config?rev={revision}'.format(schema_path=schema_path, revision=revision)
        # printing here just to reproduce master branch behavior, ideally log
        logger.info("update publish state of schema %s", api)
        request_entity = {
            'published': publish
        }
        try:
            response = self.http_client.patch(api, request_entity)
        except HTTPError as e:
            reason = e.message
            if e.response.content:
                reason = json.loads(e.response.content).read("code")
            logger.error("Failure updating publish state of schema %s: %s", api, reason)
            raise NexusException(None, "Failure publishing schema {} because {}".format(api, reason))
        if response is None:
            raise NexusException(None, "Schema {} was not found".format(api))
        else:
            logger.info("Successfully updated publish status of schema in revision %i", revision)
            return response

    def deprecate(self, organization, domain, schema, version, revision=None):
        schema_path = Schema._build_schema_path(organization, domain, schema, version)
        if revision is None:
            revision = self.get_last_revision(organization, domain, schema, version)
        return self.http_client.delete('/schemas/{schema_path}?rev={revision}'.format(schema_path=schema_path, revision=revision))

    def get_last_revision(self, organization, domain, schema, version):
        return Schema.get_revision(self.read(organization, domain, schema, version))

    def list(self):
        api = '/schemas'
        response = self.http_client.read(api)
        if response.status_code > 201:
            raise ValueError("Failure listing schemas: ", response.reason)
        return json.loads(response.content)["results"]


    @staticmethod
    def get_published(schema):
        if schema is None:
            raise NexusException(None, "Revision was not found")
        return schema.read("published")

