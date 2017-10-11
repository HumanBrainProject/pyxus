import logging
import unittest

from hamcrest.library.number.ordering_comparison import greater_than

from pyxus.client import NexusClient
import pyxus.config as conf

from hamcrest import (assert_that, instance_of, has_properties, not_none)


class TestSearchForItems(unittest.TestCase):
    client = {}

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.client = NexusClient(**conf.NEXUS_ENV_LOCALHOST)

    def test_search_items(self):
        """ This test assumes specific test data - we therefore do not apply assumptions but make this test rather a manual one until we can ensure a specific testdata set. """
        result = self.client.search_instance("interneuron", limit=100)
        assert_that(len(result), greater_than(0))
        resolved = self.client.read_all_instances(result)
        for obj in resolved:
            data_url = obj.instance.get("dataurl")
            if data_url:
                print data_url.get("downloadURL")
        print resolved