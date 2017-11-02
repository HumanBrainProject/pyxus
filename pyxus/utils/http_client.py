import logging
import requests
from pyxus.payload import JSON_CONTENT
import json

from pyxus.utils.exception import NexusException

LOGGER = logging.getLogger(__name__)


class HttpClient(object):

    def __init__(self, api_root_dict):
        self.api_root_dict = api_root_dict
        self.api_root = '{scheme}://{host}/{prefix}'.format(**self.api_root_dict)

    def _request(self, method_name, endpoint_url, data=None, headers=None):
        LOGGER.debug('%s %s\n%r', method_name, endpoint_url, data)
        method = getattr(requests, method_name)
        if endpoint_url.startswith(self.api_root_dict['scheme']):
            full_url = endpoint_url
        else:
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
        if response.status_code == 404:
            return None
        elif response.status_code<300:
            return response.json()
        else:
            return response.raise_for_status()

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