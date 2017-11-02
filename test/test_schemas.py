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
        self.client = NexusClient(**conf.NEXUS_ENV_HBP_DEV)

    def test_list_schemas(self):
        """ This test assumes specific test data - we therefore do not apply assumptions but make this test rather a manual one until we can ensure a specific testdata set. """
        result = self.client.schemas.list()
        assert_that(len(result), greater_than(0))
        print result
