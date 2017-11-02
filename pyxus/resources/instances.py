import json
import logging
import re

from pyxus.resources.resource import Resource
from pyxus.utils.exception import NexusException
from pyxus.utils.search import SearchResultInstance, SearchResult

LOGGER = logging.getLogger(__name__)


class Instance(Resource):

    def create(self, organization, domain, schema, version, content):
        path = self._build_schema_path(organization, domain, schema, version)
        endpoint = '/data/{path}'.format(path=path)
        LOGGER.info("creating instance for schema %s with content %s", path, endpoint)
        response = self.http_client.post(endpoint, content)
        if response.status_code > 201:
            LOGGER.error("Was not able to create instance for schema %s due to %s", path, response.reason)

    def update(self, organization, domain, schema, version, uuid, content, revision=None):
        path = self._build_instance_path(organization, domain, schema, version, uuid)
        if revision is None:
            revision = self.get_last_revision(organization, domain, schema, version, uuid)
        endpoint = '/data/{path}?rev={rev}'.format(path=path, rev=revision)
        LOGGER.info("updating instance %s with content %s", path, endpoint)
        self.http_client.put(endpoint, content)

    def read(self, organization, domain, schema, version, uuid, revision=None):
        path = self._build_instance_path(organization, domain, schema, version, uuid)
        if revision is None:
            endpoint = '/data/{path}'.format(path=path)
        else:
            endpoint = '/data/{path}?rev={rev}'.format(path=path, rev=revision)
        return self.http_client.read(endpoint)

    def deprecate(self, organization, domain, schema, version, uuid, revision=None):
        path = self._build_instance_path(organization, domain, schema, version, uuid)
        if revision is None:
            revision = self.get_last_revision(organization, domain, schema, version, uuid)
        endpoint = '/data/{path}?rev={rev}'.format(path=path, rev=revision)
        return self.http_client.delete(endpoint)

    def resolve_all(self, list_of_search_results):
        result_list = []
        for result in list_of_search_results:
            result_list.append(self._resolve_by_search_result(result))
        return result_list

    def _resolve_by_url(self, link_url):
        response = self.http_client.read(link_url)
        return SearchResultInstance(Instance._load_instance(data_str=response.content))

    def _resolve_by_search_result(self, search_result):
        if search_result is not None:
            link_url = self._get_self_link(search_result.self_link)
            return self._resolve_by_url(link_url)
        return None

    def search(self, term, offset=0, limit=10):
        """search for instances matching a full-text search term

        Arguments:
        term -- a full-text search term
        offset -- pagination control for page offset
        limit -- pagination control for page size
        Returns:
        a list of SearchResult objects
        """
        api = '/data?q={}&offset={}&limit={}'.format(term, offset, limit)
        response = self.http_client.read(api)
        if response.status_code < 400:
            results = json.loads(response.content)['results']
            return [SearchResult(r) for r in results]
        else:
            raise NexusException(response.status_code, response.reason)

    def get_last_revision(self, organization, domain, schema, version, id):
        return Resource.get_revision(self.read(organization, domain, schema, version, id))

    def _get_self_link(self, self_link):
        expected_host = self.http_client.api_root.replace(self.http_client.api_root_dict.read('scheme') + "://" + self.http_client.api_root_dict.read('host') + "/",
                                                           "http://kg.*?/")
        # this replacement is to fix that the service returns a wrong host
        return re.sub(expected_host, self.http_client.api_root, self_link)

    @staticmethod
    def _logical_xor(x, y):
        return not (bool(x) ^ bool(y))

    @staticmethod
    def _is_none(x):
        return x is None

    @staticmethod
    def _load_instance(data_file=None, data_str=None):
        """Load a Nexus instance from a json file.

        Arguments:
        Keyword arguments:
        data_file -- path or file for the location of the .json
        instance in JSON-LD format.
        data_str -- string data payload
        NOTE: only one of data_file or data_str should be specified
        """
        if Instance._logical_xor(Instance._is_none(data_file), Instance._is_none(data_str)):
            raise ValueError('Only one of data_file \
            or data_str can be specified')

        if data_file is not None:
            if isinstance(data_file, file):
                j = json.load(data_file)
            elif isinstance(data_file, str):
                j = json.load(open(data_file))
            else:
                raise ValueError('data_file must be of type file or string.')
        else:
            j = json.loads(data_str)

        return j



