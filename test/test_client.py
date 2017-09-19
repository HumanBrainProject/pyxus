
from pyxus.client import NexusClient

import glob
import unittest
import pyxus.config as conf
import pyxus.util as u

from hamcrest import (assert_that, instance_of, has_properties, not_none)

class TestClient(unittest.TestCase):

    def setUp(self):
        self.client_localhost = NexusClient(**conf.NEXUS_ENV_LOCALHOST)
        self.client_hbp_prod = NexusClient(**conf.NEXUS_ENV_HBP_PROD)
        self.client_hbp_dev = NexusClient(**conf.NEXUS_ENV_HBP_DEV)
        self.client_bbp_dev = NexusClient(**conf.NEXUS_ENV_BBP_DEV)

    def test_client_is_instantiable(self):
        assert_that(self.client_localhost, not_none())

    def test_client_envs(self):
        assert_that(self.client_localhost.api_root, 'http://localhost:8080/v0')
        assert_that(self.client_hbp_prod.api_root, 'https://nexus.humanbrainproject.eu/v0')
        assert_that(self.client_hbp_dev.api_root, 'https://nexus-dev.humanbrainproject.eu/v0')
        assert_that(self.client_bbp_dev.api_root, 'https://bbp-nexus.epfl.ch/dev/v0')

if __name__ == '__main__':
    unittest.main()
    # a = TestClient('test_parse')
    # a.test_client_construct()
    # a.test_client_is_instantiable()
    # a.test_client_envs()
