import logging
import uuid
from unittest import TestCase

from hamcrest.core.core.isequal import equal_to
from hamcrest.core.core.isinstanceof import instance_of
from hamcrest.core.core.isnone import not_none, none
from hamcrest.core.core.isnot import is_not
from hamcrest.library.number.ordering_comparison import greater_than, less_than

from pyxus.client import NexusClient
from pyxus.resources.entity import Domain, SearchResultList
from pyxus.resources.repository import DomainRepository
from hamcrest import (assert_that)


class TestDomainRepository(TestCase):

    default_prefix = "hbp"

    @staticmethod
    def _assert_valid_default_entity(result, identifier="hbp/core"):
        assert_that(result, instance_of(Domain))
        assert_that(result.data, not_none())
        assert_that(result.get_revision(), greater_than(0))
        assert_that(result.id, equal_to(identifier))
        assert_that(result.path, equal_to("/domains/" + identifier))

    @staticmethod
    def _assert_valid_search_list_result(search, expected_length=None):
        assert_that(search, not_none())
        assert_that(search, instance_of(SearchResultList))
        assert_that(search.results, not_none())
        if expected_length is not None:
            assert_that(len(search.results), expected_length)

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.repository = DomainRepository(NexusClient()._http_client)

    def test_read_latest_revision(self):
        result = self.repository.read(self.default_prefix, "core")
        self._assert_valid_default_entity(result)

    def test_read_revision_one(self):
        result = self.repository.read(self.default_prefix, "core", 1)
        self._assert_valid_default_entity(result)
        assert_that(result.get_revision(), equal_to(1))

    def test_read_unknown(self):
        result = self.repository.read("acme_corp", "core")
        assert_that(result, none())

#   ATTENTION: This test creates entities with random names. The execution of the test therefore increases data volume
    def test_create_and_deprecate(self):
        random_name = "{}".format(uuid.uuid4()).replace("-", "")
        entity = Domain.create_new(self.default_prefix, random_name, "Test driven creation of a domain")
        result = self.repository.create(entity)
        assert_that(result, equal_to(entity))
        self._assert_valid_default_entity(result, self.default_prefix+"/"+random_name)
        assert_that(result.get_revision(), equal_to(1))
        self._test_deprecate(entity)

    def _test_deprecate(self, entity):
        # deprecate organization
        result = self.repository.delete(entity)
        self._assert_valid_default_entity(result, entity.id)
        assert_that(result.get_revision(), equal_to(2))

    def test_update(self):
        entity = self.repository.read(self.default_prefix, "core")
        initial_description = entity.get_data("description")
        entity.data["description"] = "New description"
        entity = self.repository.update(entity)
        assert_that(entity.get_data("description"), is_not(equal_to(initial_description)))
        entity.data["description"] = initial_description
        self.repository.update(entity)

    def test_search_fulltext(self):
        search = self.repository.list(full_text_query="Domain")
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
