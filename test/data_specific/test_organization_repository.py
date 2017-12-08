import logging
import uuid
from unittest import TestCase

from hamcrest.core.core.isequal import equal_to
from hamcrest.core.core.isinstanceof import instance_of
from hamcrest.core.core.isnone import not_none, none
from hamcrest.core.core.isnot import is_not
from hamcrest.library.number.ordering_comparison import greater_than, less_than

from pyxus.resources.entity import Organization, SearchResultList
from pyxus.utils.http_client import HttpClient
from pyxus.resources.repository import OrganizationRepository
import pyxus.config as conf
from hamcrest import (assert_that)


class TestOrganizationRepository(TestCase):

    @staticmethod
    def _assert_valid_default_entity(result, identifier):
        assert_that(result, instance_of(Organization))
        assert_that(result.data, not_none())
        assert_that(result.get_revision(), greater_than(0))
        assert_that(result.id, equal_to(identifier))
        assert_that(result.path, equal_to("/organizations/" + identifier))

    @staticmethod
    def _assert_valid_search_list_result(search, expected_length=None):
        assert_that(search, not_none())
        assert_that(search, instance_of(SearchResultList))
        assert_that(search.results, not_none())
        if expected_length is not None:
            assert_that(len(search.results), expected_length)


    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.repository = OrganizationRepository(HttpClient(conf.NEXUS_ENV_LOCALHOST))

    def test_read_latest_revision(self):
        result = self.repository.read("hbp")
        self._assert_valid_default_entity(result, "hbp")

    def test_read_revision_one(self):
        result = self.repository.read("hbp", 1)
        self._assert_valid_default_entity(result, "hbp")
        assert_that(result.get_revision(), equal_to(1))

    def test_read_unknown(self):
        result = self.repository.read("acme_corp")
        assert_that(result, none())

#   ATTENTION: This test creates organizations with random names. due to the restriction of 5 characters, this set is limited and could cause collisions
    def test_create_and_deprecate(self):
        random_org = "{}".format(uuid.uuid4())[:5]
        entity = Organization.create_new(random_org, "Test driven creation of an organization")
        result = self.repository.create(entity)
        assert_that(result, equal_to(entity))
        self._assert_valid_default_entity(result, random_org)
        assert_that(result.get_revision(), equal_to(1))
        self._test_deprecate(entity)

    def _test_deprecate(self, org):
        # deprecate organization
        result = self.repository.delete(org)
        self._assert_valid_default_entity(result, org.id)
        assert_that(result.get_revision(), equal_to(2))

    def test_update(self):
        entity = self.repository.read("hbp")
        initial_description = entity.get_data("description")
        entity.data["schema:description"] = "New description"
        entity = self.repository.update(entity)
        assert_that(entity.get_data("description"), is_not(equal_to(initial_description)))
        entity.data["schema:description"] = initial_description
        self.repository.update(entity)

    def test_search_fulltext(self):
        search = self.repository.list(full_text_query="hbp")
        assert_that(search, not_none())
        assert_that(search, instance_of(SearchResultList))
        assert_that(search.results, not_none())
        assert_that(len(search.results), 1)

    def test_search_limit(self):
        search = self.repository.list(size=1)
        assert_that(search, not_none())
        assert_that(search, instance_of(SearchResultList))
        assert_that(search.results, not_none())
        assert_that(len(search.results), 1)
        assert_that(len(search.results), less_than(search.total))

    def test_list_default(self):
        search = self.repository.list()
        assert_that(search, not_none())
        assert_that(search, instance_of(SearchResultList))
        assert_that(search.results, not_none())
        assert_that(len(search.results), greater_than(0))

    def test_list_organizations_incl_deprecated(self):
        search = self.repository.list(deprecated=None)
        assert_that(search, not_none())
        assert_that(search, instance_of(SearchResultList))
        assert_that(search.results, not_none())
        assert_that(len(search.results), greater_than(0))

    def test_list_organizations_and_resolve_first(self):
        search = self.repository.list()
        assert_that(search, not_none())
        assert_that(search, instance_of(SearchResultList))
        assert_that(search.results, not_none())
        assert_that(len(search.results), greater_than(0))

        result = self.repository.resolve(search.results[0])
        assert_that(result, not_none())
        assert_that(result, instance_of(Organization))

    def test_list_organizations_and_resolve_all(self):
        search = self.repository.list()
        assert_that(search, not_none())
        assert_that(search.results, not_none())
        assert_that(len(search.results), greater_than(0))

        result = self.repository.resolve_all(search)
        assert_that(result, not_none())
        assert_that(result, instance_of(list))
        assert_that(len(result), greater_than(0))
        assert_that(result[0], instance_of(Organization))
        assert_that(result[0].data, not_none())
