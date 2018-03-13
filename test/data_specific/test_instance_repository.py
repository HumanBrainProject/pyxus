import logging
from unittest import TestCase

from hamcrest.core.core.isequal import equal_to
from hamcrest.core.core.isinstanceof import instance_of
from hamcrest.core.core.isnone import not_none, none
from hamcrest.library.number.ordering_comparison import greater_than, less_than

from pyxus.client import NexusClient
from pyxus.resources.entity import SearchResultList,  Instance
from pyxus.utils.http_client import HttpClient
from pyxus.resources.repository import InstanceRepository
import pyxus.config as conf
from hamcrest import (assert_that)



class TestInstanceRepository(TestCase):

    default_prefix = "hbp"

    def _get_instance_uuid(self):
        single_result = self.repository.list(subpath="/hbp/core/schematest/v0.0.1", size=1, deprecated=None)
        instance = single_result.results[0]
        return InstanceRepository._extract_uuid(instance.result_id)

    @staticmethod
    def _assert_valid_default_entity(result, identifier):
        assert_that(result, instance_of(Instance))
        assert_that(result.data, not_none())
        assert_that(result.get_revision(), greater_than(0))
        assert_that(result.id, equal_to(identifier))
        assert_that(result.path, equal_to("/data/" + identifier))

    @staticmethod
    def _assert_valid_search_list_result(search, expected_length=None):
        assert_that(search, not_none())
        assert_that(search, instance_of(SearchResultList))
        assert_that(search.results, not_none())
        if expected_length is not None:
            assert_that(len(search.results), expected_length)

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.repository = InstanceRepository(NexusClient()._http_client)

    def test_read_latest_revision(self):
        uuid = self._get_instance_uuid()
        result = self.repository.read(self.default_prefix, "core", "schematest", "v0.0.1", uuid)
        self._assert_valid_default_entity(result, "hbp/core/schematest/v0.0.1/"+uuid)

    def test_read_revision_one(self):
        uuid = self._get_instance_uuid()
        result = self.repository.read(self.default_prefix, "core", "schematest", "v0.0.1", uuid, 1)
        self._assert_valid_default_entity(result, "hbp/core/schematest/v0.0.1/"+uuid)
        assert_that(result.get_revision(), equal_to(1))

    def test_read_unknown(self):
        result = self.repository.read("acme_corp", "core", "schematest", "v0.0.1", "something")
        assert_that(result, none())

#   ATTENTION: This test creates entities. The execution of the test therefore increases data volume
    def test_create_and_deprecate(self):
        entity = Instance.create_new(self.default_prefix, "core", "schematest", "v0.0.1", self.test_instance)
        result = self.repository.create(entity)
        assert_that(result, equal_to(entity))
        self._assert_valid_default_entity(result, entity.id)
        assert_that(result.get_revision(), equal_to(1))
        self._test_deprecate(entity)

    def _test_deprecate(self, entity):
        # deprecate organization
        result = self.repository.delete(entity)
        self._assert_valid_default_entity(result, entity.id)
        assert_that(result.get_revision(), equal_to(2))

    def test_update(self):
        entity = self.repository.read(self.default_prefix, "core", "schematest", "v0.0.1", self._get_instance_uuid())
        entity.data["description"] = "New description"
        entity = self.repository.update(entity)
        assert_that(entity.get_data("description"), not_none())
        entity.data["description"] = None
        self.repository.update(entity)

    def test_search_fulltext(self):
        search = self.repository.list(full_text_query="Test")
        self._assert_valid_search_list_result(search, 1)

    def test_search_limit(self):
        search = self.repository.list(size=1)
        self._assert_valid_search_list_result(search, 1)
        assert_that(len(search.results), less_than(search.total))

    def test_list_default(self):
        search = self.repository.list()
        self._assert_valid_search_list_result(search)
        assert_that(len(search.results), greater_than(0))

    def test_list_incl_deprecated(self):
        search = self.repository.list(deprecated=None)
        self._assert_valid_search_list_result(search)
        assert_that(len(search.results), greater_than(0))

    def test_list_and_resolve_first(self):
        search = self.repository.list()
        self._assert_valid_search_list_result(search)
        assert_that(len(search.results), greater_than(0))

        result = self.repository.resolve(search.results[0])
        self._assert_valid_default_entity(result, result.id)

    def test_list_and_resolve_all(self):
        search = self.repository.list()
        self._assert_valid_search_list_result(search)
        assert_that(len(search.results), greater_than(0))

        result = self.repository.resolve_all(search)
        assert_that(result, not_none())
        assert_that(result, instance_of(list))
        assert_that(len(result), greater_than(0))
        self._assert_valid_default_entity(result[0], result[0].id)

    def test_list_resolved(self):
        search = self.repository.list(resolved=True)
        self._assert_valid_search_list_result(search)
        assert_that(len(search.results), greater_than(0))

    test_instance = {
      "hbp:hello_world": "Test",
      "@context": [{
        "hbp": "http://nexus.example.com/v0/vocab/hbp/core/schematest/",
        "@vocab": "http://localhost:8080/vocab/hbp/core/celloptimization/"
      }],
      "@type": "hbp:SchemaTestEntity"
    }

    def test_find_by_field(self):
        search = self.repository.find_by_field("/minds/core/activity/v0.0.1", "http://schema.org/identifier", "NCRMI_210")
        print search