# encoding: utf-8
from hamcrest.core.core.isequal import equal_to
import logging
import unittest

from hamcrest import (assert_that)

LOGGER = logging.getLogger(__name__)

class TestClient(unittest.TestCase):

    client = {}

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def test_version_check(self):
        assert_that(self.client['localhost'].version_check(), equal_to(True))