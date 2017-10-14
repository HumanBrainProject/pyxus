import json
import requests
import logging
import re
from pyxus.payload import NexusPayload, JSON_CONTENT

LOGGER = logging.getLogger(__name__)


def logical_xor(x, y):
    return not(bool(x) ^ bool(y))


def is_none(x):
    return x is None


def build_schema_path(schema_organization, schema_domain, schema_name, schema_version):
    return "{}/{}/{}/{}".format(schema_organization, schema_domain, schema_name, schema_version)


class SearchResult(object):
    score = 0.0
    result_id = None
    schema = None
    self_link = None

    def __init__(self, result_dict):
        self.result_id = result_dict['resultId']
        self.score = result_dict['score']

        links = result_dict['source']['links']
        schema_list = [x['href'] for x in links if x['rel'] == 'schema']
        self.self_link = str([x['href'] for x in links if x['rel'] == 'self'][0])
        assert(len(schema_list) == 1)
        self.schema = schema_list.pop()

    def __unicode__(self):
        '(result_id:{},schema:{}'.format(self.result_id, self.schema)

class SearchResultInstance(object):

    raw_result = None
    instance = None

    def __init__(self, raw_result):
        self.raw_result = raw_result
        self.instance = self.__simplifyResult(raw_result)

    def __simplifyResult(self, json):
        simple = {}
        for key in json:
            if not key.startswith("@"):
                new_key = re.sub(".*?:", "", key)
                if type(json[key]) is dict:
                    simple[new_key] = self.__simplifyResult(json[key])
                else:
                    simple[new_key] = json[key]
        return simple




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
        if type(data) is dict:
            data = json.dumps(data)
        headers = headers or {}
        headers.update(JSON_CONTENT)
        LOGGER.debug('request:%s %s\n%r', method_name, full_url, data)
        response = method(full_url, data, headers=headers)
        LOGGER.debug('returned %s %s', response.status_code, response.content)
        return response

    @staticmethod
    def _direct_request(method_name, full_url, data=None, headers=None):
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
            "@context": {
                "schema": "http://schema.org/"
            },
            "schema:name": name
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

    def read_schema(self, schema_path):
        api = '/schemas/{schema_path}'.format(schema_path=schema_path)
        return self.get(api)

    def upload_schema(self, schema_path, content):
        api = '/schemas/{schema_path}'.format(schema_path=schema_path)
        # printing here just to reproduce master branch behavior, ideally log
        LOGGER.info("uploading schema to %s", api)
        response = self.put(api, json.dumps(content))
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

    def publish_schema(self, schema_path, revision, publish=True):
        api = '/schemas/{schema_path}/config?rev={revision}'.format(schema_path=schema_path, revision=revision)
        # printing here just to reproduce master branch behavior, ideally log
        LOGGER.info("publishing schema %s", api)
        request_entity = {
            'published': publish
        }
        response = self.patch(api, json.dumps(request_entity))
        if response.status_code > 201:
            LOGGER.info("Failure publishing schema (%s)", api)
            LOGGER.info("Code:%s (%s) - %s", response.status_code,
                        response.reason, response.text)
            return False
        else:
            revision = json.loads(response.content).get("rev")
            LOGGER.info("Successfully published schema in revision %i", revision)
            return revision

    def create_schema(self, schema_organization, schema_domain, schema_name, schema_version, content, force_domain_creation):
        if force_domain_creation:
            if(self.read_org(schema_organization).status_code>201):
                LOGGER.info("Creation of organization %s triggered by schema definition", schema_organization)
                self.create_org(schema_organization, "Organization created by schema {}. TODO: create better description".format(schema_name))
            if(self.read_domain(schema_organization, schema_domain).status_code>201):
                LOGGER.info("Creation of domain %s in organization %s triggered by schema definition", schema_organization, schema_domain)
                self.create_domain(schema_organization, schema_domain, "Domain created by schema {}. TODO: create better description".format(schema_name))
        revision = self.upload_schema(build_schema_path(schema_organization, schema_domain, schema_name, schema_version), content)
        if revision:
            return revision
        return False


class InstanceCRUD(object):

    @staticmethod
    def load_instance(data_file=None, data_str=None):
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

    def create_instance(self, schema_path, content):
        api = '/data/{schema_path}'.format(schema_path=schema_path)
        LOGGER.info("creating instance for schema %s with content %s", schema_path, api)
        response = self.post(api, content)
        if response.status_code > 201:
            LOGGER.error("Was not able to create instance for schema %s due to %s", schema_path, response.reason)

    def read_all_instances(self, list_of_search_results):
        l = []
        for result in list_of_search_results:
            l.append(self.read_instance(search_result=result))
        return l

    def get_self_link(self, self_link):
        expected_host = self.api_root.replace(self.api_root_dict.get('scheme')+"://"+self.api_root_dict.get('host')+"/", "http://kg.*?/")
        #this replacement is to fix that the service returns a wrong host
        return re.sub(expected_host, self.api_root, self_link)

    def read_instance(self, link_url=None, search_result=None):
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

        if logical_xor(is_none(link_url), is_none(search_result)):
            raise ValueError('only one of result_id and \
            search_result arguments can be specified')

        if search_result is not None:
            link_url = self.get_self_link(search_result.self_link)

        response = self._direct_request('get', link_url)
        return SearchResultInstance(self.load_instance(data_str=response.content))

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
