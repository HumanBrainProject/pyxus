#   Copyright 2018 HumanBrainProject
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging
import unittest

from hamcrest.library.number.ordering_comparison import greater_than

from pyxus.client import NexusClient

from hamcrest import (assert_that)
from pyxus.test import env_setup

class TestSearchForItems(unittest.TestCase):
    client = {}

    def setUp(self):
        env_setup.load_env()
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