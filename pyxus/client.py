import json
import logging

from pyxus.resources.domains import Domain
from pyxus.resources.instances import Instance
from pyxus.resources.organizations import Organization
from pyxus.resources.schemas import Schema
from pyxus.utils.exception import NexusException
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
        self.domain = Domain(self._http_client)
        self.organization = Organization(self._http_client)
        self.instance = Instance(self._http_client)
        self.schema = Schema(self._http_client, self.domain, self.organization)

    def version_check(self, supported_versions=SUPPORTED_VERSIONS):
        server_metadata_url = '{scheme}://{host}/'.format(
            **self.api_root_dict)

        response = self._http_client.get(server_metadata_url)

        if response.status_code < 400:
            meta = json.loads(response.content)
            service_name = meta.get('name')
            self.version = meta.get('version')
            self.env = meta.get('env')

            if service_name == 'kg' and self.version in supported_versions:
                LOGGER.info('Version supported : %s\nenv: %s',
                            self.version, self.env)
                return True
            else:
                LOGGER.error('**Version unsupported**: %s\nenv: %s',
                             self.version, self.env)
                return True
        else:
            raise NexusException(response.status_code,
                                 response.reason)
