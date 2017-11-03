# encoding: utf-8

from pyxus.client import NexusClient

import json
import logging
import unittest
import pyxus.config as conf
import sys,os

from hamcrest import (assert_that, not_none)

LOGGER = logging.getLogger(__name__)

class TestClient(unittest.TestCase):

    client = {}

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.client['localhost'] = NexusClient(**conf.NEXUS_ENV_LOCALHOST)
        self.client['hbp_prod'] = NexusClient(**conf.NEXUS_ENV_HBP_PROD)
        self.client['hbp_dev'] = NexusClient(**conf.NEXUS_ENV_HBP_DEV)
        self.client['bbp_dev'] = NexusClient(**conf.NEXUS_ENV_BBP_DEV)

    def test_client_is_instantiable(self):
        for client in self.client.values():
            assert_that(client, not_none())

    def test_client_envs(self):
        #explicitly test that the endpoints match the expected value
        assert_that(self.client['localhost']._http_client.api_root, 'http://localhost:8080/v0')
        assert_that(self.client['hbp_prod']._http_client.api_root, 'https://nexus.humanbrainproject.eu/v0')
        assert_that(self.client['hbp_dev']._http_client.api_root, 'https://nexus-dev.humanbrainproject.eu/v0')
        assert_that(self.client['bbp_dev']._http_client.api_root, 'https://bbp-nexus.epfl.ch/dev/v0')
