from unittest import TestCase

from hamcrest.core import assert_that
from hamcrest.core.core.isequal import equal_to

from pyxus.test import env_setup
from pyxus.utils.http_client import HttpClient

class TestHttpClient(TestCase):

    def setUp(self):
        env_setup.load_env()

    def test__transform_url_to_defined_endpoint(self):
        client = HttpClient("http://foo", "v0")
        result = client.transform_url_to_defined_endpoint("https://nexus-dev.humanbrainproject.org/v0/data/something")
        print result
        assert_that(result, equal_to("http://foo/v0/data/something"))