import logging
import os

from pyxus import ENV_VAR_BLAZEGRAPH
from pyxus.config import ENV_VAR_NEXUS_PREFIX, ENV_VAR_NEXUS_NAMESPACE, ENV_VAR_NEXUS_ENDPOINT
from pyxus.resources.repository import DomainRepository, OrganizationRepository, InstanceRepository, SchemaRepository, ContextRepository
from pyxus.utils.http_client import HttpClient
LOGGER = logging.getLogger(__package__)

class NexusClient(object):
    SUPPORTED_VERSIONS = ['0.6.2']

    @staticmethod
    def get_endpoint():
        return os.environ.get(ENV_VAR_NEXUS_ENDPOINT)

    @staticmethod
    def get_blazegraph_endpoint():
        return os.environ.get(ENV_VAR_BLAZEGRAPH)

    @staticmethod
    def get_prefix():
        return os.environ.get(ENV_VAR_NEXUS_PREFIX)

    @staticmethod
    def get_namespace():
        return os.environ.get(ENV_VAR_NEXUS_NAMESPACE)

    @staticmethod
    def get_vocab():
        return "{}/voc".format(NexusClient.get_namespace())

    @staticmethod
    def get_uuid_predicate():
        return "{}/nexus/core/uuid".format(NexusClient.get_vocab())

    def __init__(self):
        self.version = None
        self.env = None
        self._http_client = HttpClient(NexusClient.get_endpoint(), NexusClient.get_prefix())
        self.domains = DomainRepository(self._http_client)
        self.contexts = ContextRepository(self._http_client)
        self.organizations = OrganizationRepository(self._http_client)
        self.instances = InstanceRepository(self._http_client)
        self.schemas = SchemaRepository(self._http_client)

    def version_check(self, supported_versions=SUPPORTED_VERSIONS):
        server_metadata_url = '{}/'.format(NexusClient.get_endpoint())

        response = self._http_client.get(server_metadata_url)

        if response is not None:
            service_name = response.get('name')
            self.version = response.get('version')
            self.env = response.get('env')
            if service_name == 'kg' and self.version in supported_versions:
                LOGGER.info('Version supported : %s\nenv: %s',
                            self.version, self.env)
                return True
            else:
                LOGGER.error('**Version unsupported**: %s\nenv: %s',
                             self.version, self.env)
                return True
        else:
            raise NexusException(response.reason)

    def get_fullpath_for_entity(self, entity):
        return "{}{}".format(NexusClient.get_namespace(), entity.path)


class NexusException(Exception):
    """Exception raised when a Nexus call fails

    Attributes:
    http_status_code -- code returned by the API
    message -- message for the exception
    """
    def __init__(self, message):
        self.message = message
