import logging
from unittest import TestCase

from hamcrest.core.assert_that import assert_that
from hamcrest.core.core.isequal import equal_to

from pyxus.resources.entity import Entity, Schema


class TestEntity(TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def test_extract_id_from_url(self):
        result = Entity.extract_id_from_url("http://kg:8080/v0/schemas/hbp/core/celloptimization/v0.0.1", Schema.path)
        assert_that(result, equal_to("hbp/core/celloptimization/v0.0.1"))

    def test_extract_id_from_url_with_param(self):
        result = Entity.extract_id_from_url("http://kg:8080/v0/schemas/hbp/core/celloptimization/v0.0.1?hello_world", Schema.path)
        assert_that(result, equal_to("hbp/core/celloptimization/v0.0.1"))

    def test_extract_id_from_url_with_anchor(self):
        result = Entity.extract_id_from_url("http://kg:8080/v0/schemas/hbp/core/celloptimization/v0.0.1#hello_world", Schema.path)
        assert_that(result, equal_to("hbp/core/celloptimization/v0.0.1"))

    def test_extract_id_from_url_with_slash_at_the_end(self):
        result = Entity.extract_id_from_url("http://kg:8080/v0/schemas/hbp/core/celloptimization/v0.0.1/", Schema.path)
        assert_that(result, equal_to("hbp/core/celloptimization/v0.0.1"))

    def test_extract_id_from_url_with_wrong_entity(self):
        with self.assertRaises(ValueError):
            Entity.extract_id_from_url("http://kg:8080/v0/organizations/hbp/core/celloptimization/v0.0.1", Schema.path)
