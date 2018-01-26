import logging
import unittest

from hamcrest.library.number.ordering_comparison import greater_than

from pyxus.client import NexusClient
import pyxus.config as conf

from hamcrest import (assert_that, instance_of, has_properties, not_none, equal_to)


class TestSearchForItems(unittest.TestCase):
    client = {}

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.client = NexusClient()

    def test_search_items(self):
        """ This test assumes specific test data - we therefore do not apply assumptions but make this test rather a manual one until we can ensure a specific testdata set. """
        search = self.client.instances.list(full_text_query="interneuron")
        assert_that(len(search.results), greater_than(0))
        results = self.client.instances.resolve_all(search)
        print results
        for r in results:
            data_url = r.get_data("dataurl")
            if data_url:
                print data_url["downloadURL"]