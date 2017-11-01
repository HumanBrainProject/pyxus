import json
import logging
import re

from pyxus.utils.exception import NexusException
from pyxus.utils.search import SearchResultInstance, SearchResult

LOGGER = logging.getLogger(__name__)


class Instance(object):
    def __init__(self, http_client):
        self._http_client = http_client

    def create(self, schema_path, content):
        api = '/data/{schema_path}'.format(schema_path=schema_path)
        LOGGER.info("creating instance for schema %s with content %s", schema_path, api)
        response = self._http_client.post(api, content)
        if response.status_code > 201:
            LOGGER.error("Was not able to create instance for schema %s due to %s", schema_path, response.reason)

    def read_all(self, list_of_search_results):
        result_list = []
        for result in list_of_search_results:
            result_list.append(self.read(search_result=result))
        return result_list

    def read(self, link_url=None, search_result=None):
        """read an instance from a result_id URI or a SearchResult object

        Arguments:
        Keyword arguments:
        result_id -- URI to the instance we want to retrieve and decode
        search_result -- SearchResult object which corresponds to the
        object we want to fetch used
        Returns:
        a dict representing the instance using JSON-LD conventions
        for keys and values
        """

        if Instance._logical_xor(Instance._is_none(link_url), Instance._is_none(search_result)):
            raise ValueError('only one of result_id and \
            search_result arguments can be specified')

        if search_result is not None:
            link_url = self._get_self_link(search_result.self_link)
        response = self._http_client.get(link_url)
        return SearchResultInstance(Instance._load_instance(data_str=response.content))

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
        response = self._http_client.get(api)
        if response.status_code < 400:
            results = json.loads(response.content)['results']
            return [SearchResult(r) for r in results]
        else:
            raise NexusException(response.status_code, response.reason)

    def _get_self_link(self, self_link):
        expected_host = self._http_client.api_root.replace(self._http_client.api_root_dict.get('scheme') + "://" + self._http_client.api_root_dict.get('host') + "/",
                                                           "http://kg.*?/")
        # this replacement is to fix that the service returns a wrong host
        return re.sub(expected_host, self._http_client.api_root, self_link)

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
