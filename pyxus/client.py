import logging
import os

from pyxus.resources.repository import DomainRepository, OrganizationRepository, InstanceRepository, SchemaRepository, ContextRepository
from pyxus.utils.http_client import HttpClient

LOGGER = logging.getLogger(__package__)

ENV_VAR_NEXUS_ENDPOINT = "NEXUS_ENDPOINT"
ENV_VAR_NEXUS_PREFIX = "NEXUS_PREFIX"
ENV_VAR_NEXUS_NAMESPACE = "NEXUS_NAMESPACE"

class NexusClient(object):
    SUPPORTED_VERSIONS = ['0.8.14']

    def __init__(self, scheme=None, host=None, prefix=None, alternative_namespace=None, token=None):
        self.version = None
        self.namespace =         self.env = None
        self.config = NexusConfig(scheme, host, prefix, alternative_namespace)
        self._http_client = HttpClient(self.config.NEXUS_ENDPOINT, self.config.NEXUS_PREFIX, token=token)
        self.domains = DomainRepository(self._http_client)
        self.contexts = ContextRepository(self._http_client)
        self.organizations = OrganizationRepository(self._http_client)
        self.instances = InstanceRepository(self._http_client)
        self.schemas = SchemaRepository(self._http_client)

    def version_check(self, supported_versions=SUPPORTED_VERSIONS):
        server_metadata_url = '{}/'.format(self.config.NEXUS_ENDPOINT)

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
        return "{}{}".format(self.config.NEXUS_NAMESPACE, entity.path)


class NexusConfig(object):

    def __init__(self, scheme=None, host=None, nexus_prefix=None, nexus_namespace=None):
       if host is None and scheme is None and ENV_VAR_NEXUS_ENDPOINT in os.environ:
           self.NEXUS_ENDPOINT = os.environ.get(ENV_VAR_NEXUS_ENDPOINT)
       elif host is not None and scheme is not None:
           self.NEXUS_ENDPOINT = "{}/{}".format(scheme, host)
       else:
           self.NEXUS_ENDPOINT = None
       self.NEXUS_PREFIX = os.environ.get(ENV_VAR_NEXUS_PREFIX) if nexus_prefix is None and ENV_VAR_NEXUS_PREFIX in os.environ  else nexus_prefix
       if nexus_namespace is None and ENV_VAR_NEXUS_NAMESPACE in os.environ:
            self.NEXUS_NAMESPACE = os.environ.get(ENV_VAR_NEXUS_NAMESPACE)
       else:
           self.NEXUS_NAMESPACE = None
       self._validate()

    def _validate(self):
        if self.NEXUS_ENDPOINT is None:
            raise ValueError("The Nexus endpoint is not set!")
        if self.NEXUS_PREFIX is None:
            raise ValueError("The Nexus prefix is not set!")
        if self.NEXUS_NAMESPACE is None:
            raise ValueError("The Nexus namespace is not set!")


class NexusException(Exception):
    """Exception raised when a Nexus call fails

    Attributes:
    http_status_code -- code returned by the API
    message -- message for the exception
    """
    def __init__(self, message):
        self.message = message
