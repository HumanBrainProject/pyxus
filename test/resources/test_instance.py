from unittest import TestCase
from pyxus.resources.instances import Instance
from pyxus.utils.http_client import HttpClient
import pyxus.config as conf
from hamcrest import (assert_that)

class TestInstance(TestCase):

    def setUp(self):
        self.instance = Instance(HttpClient(conf.NEXUS_ENV_LOCALHOST))

    def test_read(self):
        result = self.instance.read("hbp/core/celloptimization/v0.0.1", "33fd65de-912b-43f6-8b14-6c6b5e0939e9")
        assert_that(result is not None)
        assert_that(result.read("deprecated") is not None)

    def test_read_inexistant(self):
        result = self.instance.read("hbp/core/celloptimization/v0.0.1", "inexistant")
        assert_that(result is None)