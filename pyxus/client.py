import json
import requests
from typing import Union
import logging
from pyxus.payload import NexusPayload, JSON_CONTENT


LOGGER = logging.getLogger('pyxus.client')


class HTTPMixin(object):

    def _do_request(self, method_name, endpoint_url, data, headers=None):
        LOGGER.debug('%s %s\n%r', method_name, endpoint_url, data)
        method = getattr(requests, method_name)
        full_url = '{api_root}{endpoint_url}'.format(
            api_root=self.api_root,
            endpoint_url=endpoint_url
        )
        headers = headers or {}
        headers.update(self.content_mimetype)
        response = method(full_url, str(data), headers=headers)
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

    def delete(self, *args, **kwargs):
        return self._do_request('delete', *args, **kwargs)


class OrgCRUD(object):

    def put_org(self, name, desc):
        obj = {
            'description': desc
        }
        api = '/organizations/{name}'.format(name=name)
        return self.put(api, obj)


class DomainCRUD(object):

    def put_domain(self, org, dom, desc):
        obj = {
            'description': desc
        }
        api = '/organizations/{org}/domain/{dom}'.format(
            org=org,
            dom=dom
        )
        return self.put(api, obj)


class SchemeCRUD(object):

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


class CRUDMixin(OrgCRUD, DomainCRUD, SchemeCRUD):
    pass


class NexusClient(CRUDMixin, HTTPMixin):

    def __init__(self, scheme='http', host='localhost:8080', prefix='v0'):
        self.api_root = '{scheme}://{host}/{prefix}'.format(
            scheme=scheme,
            host=host,
            prefix=prefix,
        )
        self.api_root_dict = {
            'scheme': scheme,
            'host': host,
            'prefix': prefix
        }
