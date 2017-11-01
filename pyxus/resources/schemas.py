import logging
import json

LOGGER = logging.getLogger(__name__)


class Schema(object):

    def __init__(self, http_client, domain, organization):
        self.http_client = http_client
        self.domain = domain
        self.organization = organization

    def list(self):
        api = '/schemas'
        response = self.http_client.get(api)
        if response.status_code > 201:
            raise ValueError("Failure listing schemas: ", response.reason)
        return json.loads(response.content)["results"]

    def read(self, schema_path):
        api = '/schemas/{schema_path}'.format(schema_path=schema_path)
        return self.http_client.get(api)

    def upload(self, schema_path, content):
        api = '/schemas/{schema_path}'.format(schema_path=schema_path)
        # printing here just to reproduce master branch behavior, ideally log
        LOGGER.info("uploading schema to %s", api)
        response = self.http_client.put(api, json.dumps(content))
        print response.reason, response.text, response.status_code
        if response.status_code > 201:
            LOGGER.info("Failure uploading schema to %s", api)
            LOGGER.info("Code:%s (%s) - %s", response.status_code,
                        response.reason, response.text)
            LOGGER.info("payload:")
            LOGGER.info(content)
            return False
        else:
            revision = json.loads(response.content).get("rev")
            LOGGER.info("Successfully created schema in revision %i", revision)
            return revision

    def publish(self, schema_path, revision, publish=True):
        api = '/schemas/{schema_path}/config?rev={revision}'.format(schema_path=schema_path, revision=revision)
        # printing here just to reproduce master branch behavior, ideally log
        LOGGER.info("publishing schema %s", api)
        request_entity = {
            'published': publish
        }
        response = self.http_client.patch(api, json.dumps(request_entity))
        if response.status_code > 201:
            LOGGER.info("Failure publishing schema (%s)", api)
            LOGGER.info("Code:%s (%s) - %s", response.status_code,
                        response.reason, response.text)
            return False
        else:
            revision = json.loads(response.content).get("rev")
            LOGGER.info("Successfully published schema in revision %i", revision)
            return revision

    def create(self, schema_organization, schema_domain, schema_name, schema_version, content, force_domain_creation):
        if force_domain_creation:
            if self.organization.read(schema_organization).status_code > 201:
                LOGGER.info("Creation of organization %s triggered by schema definition", schema_organization)
                self.organization.create(schema_organization, "Organization created by schema {}. TODO: create better description".format(schema_name))
            if self.domain.read(schema_organization, schema_domain).status_code > 201:
                LOGGER.info("Creation of domain %s in organization %s triggered by schema definition", schema_organization, schema_domain)
                self.domain.create(schema_organization, schema_domain, "Domain created by schema {}. TODO: create better description".format(schema_name))
        revision = self.upload(Schema._build_schema_path(schema_organization, schema_domain, schema_name, schema_version), content)
        if revision:
            return revision
        return False

    @staticmethod
    def _build_schema_path(schema_organization, schema_domain, schema_name, schema_version):
        return "{}/{}/{}/{}".format(schema_organization, schema_domain, schema_name, schema_version)

    @staticmethod
    def build_schema_path_from_schema_data(schema_data):
        return Schema._build_schema_path(schema_data.organization, schema_data.domain, schema_data.schema_name, schema_data.version)
