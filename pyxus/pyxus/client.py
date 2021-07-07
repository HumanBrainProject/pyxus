#  Copyright 2018 - 2021 Swiss Federal Institute of Technology Lausanne (EPFL)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0.
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  This open source software code was developed in part or in whole in the
#  Human Brain Project, funded from the European Union's Horizon 2020
#  Framework Programme for Research and Innovation under
#  Specific Grant Agreements No. 720270, No. 785907, and No. 945539
#  (Human Brain Project SGA1, SGA2 and SGA3).


import logging
import os

from openid_http_client.http_client import HttpClient

from pyxus.resources.constants import ENV_VAR_NEXUS_ENDPOINT, ENV_VAR_NEXUS_PREFIX, ENV_VAR_NEXUS_NAMESPACE
from pyxus.resources.repository import DomainRepository, OrganizationRepository, InstanceRepository, SchemaRepository, ContextRepository


class NexusClient(object):
    SUPPORTED_VERSIONS = ('0.9.5', '0.9.8')

    def __init__(self, scheme=None, host=None, prefix=None, alternative_namespace=None, auth_client=None):
        self.version = None
        self.logger = logging.getLogger(__name__)
        self.namespace = alternative_namespace if alternative_namespace is not None else "{}://{}".format(scheme, host)
        self.env = None
        self.config = NexusConfig(scheme, host, prefix, self.namespace)
        self._http_client = HttpClient(self.config.NEXUS_ENDPOINT, self.config.NEXUS_PREFIX, auth_client=auth_client,
                                       alternative_endpoint_writing=self.config.NEXUS_NAMESPACE)
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
                self.logger.debug('Version supported : %s\nenv: %s',
                            self.version, self.env)
                return True
            self.logger.error('**Version unsupported**: %s\nenv: %s',
                         self.version, self.env)
            return False
        raise NexusException(response.reason)

    def get_fullpath_for_entity(self, entity):
        return "{}{}".format(self.config.NEXUS_NAMESPACE, entity.path)


class NexusConfig(object):

    def __init__(self, scheme=None, host=None, nexus_prefix=None, nexus_namespace=None):
        if host is None and scheme is None and ENV_VAR_NEXUS_ENDPOINT in os.environ:
            self.NEXUS_ENDPOINT = os.environ.get(ENV_VAR_NEXUS_ENDPOINT)
        elif host is not None and scheme is not None:
            self.NEXUS_ENDPOINT = "{}://{}".format(scheme, host)
        else:
            self.NEXUS_ENDPOINT = None
        self.NEXUS_PREFIX = os.environ.get(ENV_VAR_NEXUS_PREFIX) if nexus_prefix is None and ENV_VAR_NEXUS_PREFIX in os.environ else nexus_prefix
        if nexus_namespace is None and ENV_VAR_NEXUS_NAMESPACE in os.environ:
            self.NEXUS_NAMESPACE = os.environ.get(ENV_VAR_NEXUS_NAMESPACE)
        else:
            self.NEXUS_NAMESPACE = nexus_namespace
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
        super(NexusException, self).__init__(message)
        self.message = message
