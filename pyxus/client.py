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

    def put(self, *args, **kwargs):
        return self._do_request('put', *args, **kwargs)

    def get(self, *args, **kwargs):
        return self._do_request('get', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._do_request('post', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self._do_request('patch', *args, **kwargs)

    def put_org(self, name, desc):
        obj = {
            'description': desc
        }
        api = '/organizations/{name}'.format(name=name)
        return self.put(api, obj)

    def put_domain(self, org, dom, desc):
        obj = {
            'description': desc
        }
        api = '/organizations/{org}/domain/{dom}'.format(
            org=org,
            dom=dom
        )
        return self.put(api, obj)

    def put_schema(self, name, content):
        api = '/schemas{name}'.format(name=name)
        # printing here just to reproduce master branch behavior, ideally log
        LOGGER.info("uploading schema to %s", api)
        response = self.put(api, content)
        if response > 201:
            LOGGER.info("Failure uploading schema to %s", api)
            LOGGER.info("Code:%s (%s) - %s",
                response.status_code, response.reason, response.text)
            LOGGER.info("payload:")
            LOGGER.info(content)
            return False
        else:
            return True