import logging
import uuid
from unittest import TestCase

from hamcrest.core.core.isequal import equal_to
from hamcrest.core.core.isinstanceof import instance_of
from hamcrest.core.core.isnone import not_none, none
from hamcrest.library.number.ordering_comparison import greater_than, less_than

from pyxus.resources.entity import SearchResultList, Context
from pyxus.utils.http_client import HttpClient
from pyxus.resources.repository import ContextRepository
import pyxus.config as conf
from hamcrest import (assert_that)


class TestContextRepository(TestCase):
    default_prefix = "hbp"

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.repository = ContextRepository(HttpClient(conf.NEXUS_ENV_LOCALHOST))
        self._create_and_publish_testcontext()

    @staticmethod
    def _assert_valid_default_entity(result, identifier="hbp/core/testcontext/v0.0.1"):
        assert_that(result, instance_of(Context))
        assert_that(result.data, not_none())
        assert_that(result.get_revision(), greater_than(0))
        assert_that(result.id, equal_to(identifier))
        assert_that(result.path, equal_to("/contexts/" + identifier))

    @staticmethod
    def _assert_valid_search_list_result(search, expected_length=None):
        assert_that(search, not_none())
        assert_that(search, instance_of(SearchResultList))
        assert_that(search.results, not_none())
        if expected_length is not None:
            assert_that(len(search.results), expected_length)

    def test_read_latest_revision(self):
        result = self.repository.read(self.default_prefix, "core", "testcontext", "v0.0.1")
        self._assert_valid_default_entity(result)

    def test_read_revision_one(self):
        result = self.repository.read(self.default_prefix, "core", "testcontext", "v0.0.1", 1)
        self._assert_valid_default_entity(result)
        assert_that(result.get_revision(), equal_to(1))

    def test_read_unknown(self):
        result = self.repository.read("acme_corp", "core", "testcontext", "v0.0.1")
        assert_that(result, none())

    #   ATTENTION: This test creates entities with random names. The execution of the test therefore increases data volume
    def test_create_and_deprecate(self):
        random_name = "{}".format(uuid.uuid4()).replace("-", "")
        entity = Context.create_new(self.default_prefix, "core", random_name, "v0.0.1", self.test_context)
        result = self.repository.create(entity)
        assert_that(result, equal_to(entity))
        self._assert_valid_default_entity(result, self.default_prefix + "/core/" + random_name + "/v0.0.1")
        assert_that(result.get_revision(), equal_to(1))
        self._test_deprecate(entity)

    def _test_deprecate(self, entity):
        # deprecate organization
        result = self.repository.delete(entity)
        self._assert_valid_default_entity(result, entity.id)
        assert_that(result.get_revision(), equal_to(2))

    #   ATTENTION: This test creates entities with random names. The execution of the test therefore increases data volume
    def test_create_and_publish(self):
        random_name = "{}".format(uuid.uuid4()).replace("-", "")
        entity = Context.create_new(self.default_prefix, "core", random_name, "v0.0.1", self.test_context)
        result = self.repository.create(entity)
        assert_that(result, equal_to(entity))
        self._assert_valid_default_entity(result, self.default_prefix + "/core/" + random_name + "/v0.0.1")
        assert_that(result.get_revision(), equal_to(1))

        result = self.repository.publish(entity, True)
        self._assert_valid_default_entity(result, self.default_prefix + "/core/" + random_name + "/v0.0.1")
        assert_that(result.is_published(), equal_to(True))

    def test_update(self):
        entity = self.repository.read(self.default_prefix, "core", "testcontext", "v0.0.1")
        entity.data["description"] = "New description"
        entity = self.repository.update(entity)
        assert_that(entity.get_data("description"), not_none())
        entity.data["description"] = None
        self.repository.update(entity)

    def test_search_fulltext(self):
        self.test_create_and_publish()
        search = self.repository.list(full_text_query="affiliation")
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

    def _create_and_publish_testcontext(self):
        context = self.repository.read("hbp", "core", "testcontext", "v0.0.1")
        if context is None:
            context = self.repository.create(Context.create_new("hbp", "core", "testcontext", "v0.0.1", self.test_context))
        if not context.is_published():
            self.repository.publish(context, True)

    test_context = {
        "@context": {
            "schema": "http://schema.org/",
            "address": {
                "@id": "schema:address"
            },
            "PostalAddress": {
                "@id": "schema:PostalAddress"
            },
            "parentOrganization": {
                "@type": "@id",
                "@id": "schema:parentOrganization"
            },
            "telephone": {
                "@type": "xsd:string",
                "@id": "schema:telephone"
            },
            "addressCountry": {
                "@type": "xsd:string",
                "@id": "schema:addressCountry"
            },
            "addressLocality": {
                "@type": "xsd:string",
                "@id": "schema:addressLocality"
            },
            "postalCode": {
                "@type": "xsd:string",
                "@id": "schema:postalCode"
            },
            "streetAddress": {
                "@type": "xsd:string",
                "@id": "schema:streetAddress"
            },
            "name": {
                "@type": "xsd:string",
                "@id": "schema:name"
            },
            "givenName": {
                "@type": "xsd:string",
                "@id": "schema:givenName"
            },
            "email": {
                "@type": "xsd:string",
                "@id": "schema:email"
            },
            "affiliation": {
                "@type": "@id",
                "@id": "schema:affiliation"
            }
        }
    }
