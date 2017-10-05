import json
import requests
import logging
from pyxus.payload import NexusPayload, JSON_CONTENT

LOGGER = logging.getLogger(__name__)


def logical_xor(x, y):
    return not(bool(x) ^ bool(y))


def is_none(x):
    return x is None


class SearchResult(object):
    score = 0.0
    result_id = None
    schema = None

    def __init__(self, result_dict):
        self.result_id = result_dict['resultId']
        self.score = result_dict['score']
        links = result_dict['source']['links']
        schema_list = [x['href'] for x in links if x['rel'] == 'schema']
        assert(len(schema_list) == 1)
        self.schema = schema_list.pop()

    def __unicode__(self):
        '(result_id:{},schema:{}'.format(self.result_id, self.schema)


class NexusException(Exception):
    """Exception raised when a Nexus call fails

    Attributes:
    http_status_code -- code returned by the API
    message -- message for the exception
    """
    def __init__(self, http_status_code, message):
        self.http_status_code = http_status_code
        self.message = message


class HTTPMixin(object):

    def _request(self, method_name, endpoint_url, data=None, headers=None):
        LOGGER.debug('%s %s\n%r', method_name, endpoint_url, data)
        method = getattr(requests, method_name)
        full_url = '{api_root}{endpoint_url}'.format(
            api_root=self.api_root,
            endpoint_url=endpoint_url
        )
        headers = headers or {}
        headers.update(JSON_CONTENT)
        LOGGER.debug('request:%s %s\n%r', method_name, full_url, data)
        response = method(full_url, str(data), headers=headers)
        LOGGER.debug('returned %s', response.status_code)
        return response

    def _direct_request(self, method_name, full_url, data=None, headers=None):
        LOGGER.debug('%s %s\n%r', method_name, full_url, data)
        method = getattr(requests, method_name)
        headers = headers or {}
        headers.update(JSON_CONTENT)
        LOGGER.debug('request:%s %s\n%r', method_name, full_url, data)
        response = method(full_url, str(data), headers=headers)
        LOGGER.debug('returned %s', response.status_code)
        return response

    def put(self, *args, **kwargs):
        return self._request('put', *args, **kwargs)

    def get(self, *args, **kwargs):
        # return NexusPayload(response.content)?
        return self._request('get', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._request('post', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self._request('patch', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._request('delete', *args, **kwargs)


class OrgCRUD(object):

    def create_org(self, name, desc):
        obj = {
            'description': desc
        }
        api = '/organizations/{name}'.format(name=name)
        return self.put(api, json.dumps(obj))

    def read_org(self, name):
        api = '/organizations/{name}'.format(name=name)
        return self.get(api)

    def list_orgs(self, name):
        api = '/organizations/{name}'.format(name=name)
        return self.get(api)


class DomainCRUD(object):

    def create_domain(self, org, dom, desc):
        obj = {
            'description': desc
        }
        api = '/organizations/{org}/domains/{dom}'.format(
            org=org,
            dom=dom
        )
        return self.put(api, json.dumps(obj))

    def read_domain(self, org, dom):
        api = '/organizations/{org}/domains/{dom}'.format(
            org=org,
            dom=dom
        )
        return self.get(api)


class SchemaCRUD(object):

    def create_schema(self, name, content):
        api = '/schemas{name}'.format(name=name)
        # printing here just to reproduce master branch behavior, ideally log
        LOGGER.info("uploading schema to %s", api)
        response = self.put(api, json.dumps(content))
        if response > 201:
            LOGGER.info("Failure uploading schema to %s", api)
            LOGGER.info("Code:%s (%s) - %s", response.status_code,
                        response.reason, response.text)
            LOGGER.info("payload:")
            LOGGER.info(content)
            return False
        else:
            return True


class InstanceCRUD(object):
    def load_instance(self, data_file=None, data_str=None):
        """Load a Nexus instance from a json file.

        Arguments:
        Keyword arguments:
        data_file -- path or file for the location of the .json
        instance in JSON-LD format.
        data_str -- string data payload
        NOTE: only one of data_file or data_str should be specified
        """
        if logical_xor(is_none(data_file), is_none(data_str)):
            raise ValueError('Only one of data_file \
            or data_str can be specified')

        j = None
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

    def create_instance(self, name, desc):
        obj = {
            'description': desc
        }
        api = '/organizations/{name}'.format(name=name)
        return self.put(api, json.dumps(obj))

    def read_instance(self, result_id=None, search_result=None):
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

        if logical_xor(is_none(result_id), is_none(search_result)):
            raise ValueError('only one of result_id and \
            search_result arguments can be specified')

        if search_result is not None:
            result_id = search_result.result_id

        response = self._direct_request('get', result_id)
        return self.load_instance(data_str=response.content)

    def search_instance(self, term, offset=0, limit=10, filters=None):
        """search for instances matching a full-text search term

        Arguments:
        term -- a full-text search term
        offset -- pagination control for page offset
        limit -- pagination control for page size
        Keyword arguments:
        filters -- WARNING: currently ignored
        Returns:
        a list of SearchResult objects
        """
        api = '/data?q={}&offset={}&limit={}'.format(term, offset, limit)
        response = self.get(api)
        if response.status_code < 400:
            results = json.loads(response.content)['results']
            return [SearchResult(r) for r in results]
        else:
            raise NexusException(response.status_code,
                                 response.reason)


class CRUDMixin(OrgCRUD, DomainCRUD, SchemaCRUD, InstanceCRUD):
    pass


class NexusClient(CRUDMixin, HTTPMixin):

    SUPPORTED_VERSIONS = ['0.6.1']

    def __init__(self, scheme='http', host='localhost:8080', prefix='v0'):
        self.api_root_dict = {
            'scheme': scheme,
            'host': host,
            'prefix': prefix
        }
        self.api_root = '{scheme}://{host}/{prefix}'.format(
            **self.api_root_dict)

        self.version = None
        self.env = None

    def version_check(self, supported_versions=SUPPORTED_VERSIONS):
        server_metadata_url = '{scheme}://{host}/'.format(
            **self.api_root_dict)

        response = self._direct_request('get', server_metadata_url)

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
