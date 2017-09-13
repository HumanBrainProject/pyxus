import json
import requests
from typing import Union
import logging

LOGGER = logging.getLogger('pyxus.client')

JSON_CONTENT = { "Content-type" : "application/json" }

class NexusClient:

    def __init__(self,
                 scheme: str='http',
                 host: str='localhost:8080',
                 prefix: str='v0'
                 ):
        self.api_root = f'{scheme}://{host}/{prefix}'
        self.api_root_dict = {
            'scheme': scheme,
            'host': host,
            'prefix': prefix
        }

    @property
    def content_mimetype(self):
        return JSON_CONTENT

    def _do_request(self,
                    method_name: str,
                    endpoint_url: str,
                    data: Union[str, dict],
                    ):
        LOGGER.debug('%s %s\n%r', method_name, endpoint_url, data)
        method = getattr(requests, method_name)
        full_url = f'{self.api_root}{endpoint_url}'
        if isinstance(data, dict):
            data = json.dumps(data)
        headers = JSON_CONTENT
        response = method(full_url, data, headers=headers)
        LOGGER.debug('returned %s', response.status_code)
        return response

    def _put(self, *args, **kwargs):
        return self._do_request('put', *args, **kwargs)

    def put_org(self, name: str, desc: str) -> requests.Response:
        obj = {
            'description': desc
        }
        api = f'/organizations/{name}'
        return self._put(api, obj)

    def put_domain(self, org: str, dom: str, desc: str) -> requests.Response:
        obj = {
            'description': desc
        }
        api = f'/organizations/{org}/domain/{dom}'
        return self._put(api, obj)

    def put_schema(self, name: str, content: str) -> bool:
        api = f'/schemas{name}'
        # printing here just to reproduce master branch behavior, ideally log
        print("uploading schema to {}".format(api))
        response = self._put(api, content)
        if response > 201:
            print("Failure uploading schema to {}".format(api))
            print("Code:{} ({}) - {}".format(
                response.status_code, response.reason, response.text))
            print("payload:")
            print(content)
            return False
        else:
            return True