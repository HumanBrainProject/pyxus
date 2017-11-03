import json
import logging

from pyxus.resources.repository import DomainRepository, OrganizationRepository, InstanceRepository, SchemaRepository
from pyxus.utils.http_client import HttpClient

LOGGER = logging.getLogger(__name__)


class NexusClient(object):

    SUPPORTED_VERSIONS = ['0.6.2']

    def __init__(self, scheme='http', host='localhost:8080', prefix='v0'):
        self.api_root_dict = {
            'scheme': scheme,
            'host': host,
            'prefix': prefix
        }
        self.version = None
        self.env = None
        self._http_client = HttpClient(self.api_root_dict)
        self.domains = DomainRepository(self._http_client)
        self.organizations = OrganizationRepository(self._http_client)
        self.instances = InstanceRepository(self._http_client)
        self.schemas = SchemaRepository(self._http_client)

    def version_check(self, supported_versions=SUPPORTED_VERSIONS):
        server_metadata_url = '{scheme}://{host}/'.format(
            **self.api_root_dict)

        response = self._http_client.get(server_metadata_url)

        if response.status_code < 400:
            meta = json.loads(response.content)
            service_name = meta.read('name')
            self.version = meta.read('version')
            self.env = meta.read('env')

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


class NexusException(Exception):
    """Exception raised when a Nexus call fails

    Attributes:
    http_status_code -- code returned by the API
    message -- message for the exception
    """
    def __init__(self, message):
        self.message = message
