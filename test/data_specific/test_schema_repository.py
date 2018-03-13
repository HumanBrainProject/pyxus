import logging
import uuid
from unittest import TestCase

from hamcrest.core.core.isequal import equal_to
from hamcrest.core.core.isinstanceof import instance_of
from hamcrest.core.core.isnone import not_none, none
from hamcrest.library.number.ordering_comparison import greater_than, less_than

from pyxus.client import NexusClient
from pyxus.resources.entity import SearchResultList, Schema
from pyxus.utils.http_client import HttpClient
from pyxus.resources.repository import SchemaRepository
import pyxus.config as conf
from hamcrest import (assert_that)


class TestSchemaRepository(TestCase):

    default_prefix = "hbp"

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.repository = SchemaRepository(NexusClient()._http_client)
        self._create_and_publish_testschema()
        self._create_testschema_v2()

    @staticmethod
    def _assert_valid_default_entity(result, identifier="hbp/core/testschema/v0.0.1"):
        assert_that(result, instance_of(Schema))
        assert_that(result.data, not_none())
        assert_that(result.get_revision(), greater_than(0))
        assert_that(result.id, equal_to(identifier))
        assert_that(result.path, equal_to("/schemas/" + identifier))

    @staticmethod
    def _assert_valid_search_list_result(search, expected_length=None):
        assert_that(search, not_none())
        assert_that(search, instance_of(SearchResultList))
        assert_that(search.results, not_none())
        if expected_length is not None:
            assert_that(len(search.results), expected_length)


    def test_read_latest_revision(self):
        result = self.repository.read(self.default_prefix, "core", "testschema", "v0.0.1")
        self._assert_valid_default_entity(result)

    def test_read_revision_one(self):
        result = self.repository.read(self.default_prefix, "core", "testschema", "v0.0.1", 1)
        self._assert_valid_default_entity(result)
        assert_that(result.get_revision(), equal_to(1))

    def test_read_unknown(self):
        result = self.repository.read("acme_corp", "core", "testschema", "v0.0.1")
        assert_that(result, none())

#   ATTENTION: This test creates entities with random names. The execution of the test therefore increases data volume
    def test_create_and_deprecate(self):
        random_name = "{}".format(uuid.uuid4()).replace("-", "")
        entity = Schema.create_new(self.default_prefix, "core", random_name, "v0.0.1", self.test_schema)
        result = self.repository.create(entity)
        assert_that(result, equal_to(entity))
        self._assert_valid_default_entity(result, self.default_prefix+"/core/"+random_name+"/v0.0.1")
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
        entity = Schema.create_new(self.default_prefix, "core", random_name, "v0.0.1", self.test_schema)
        result = self.repository.create(entity)
        assert_that(result, equal_to(entity))
        self._assert_valid_default_entity(result, self.default_prefix + "/core/" + random_name + "/v0.0.1")
        assert_that(result.get_revision(), equal_to(1))

        result = self.repository.publish(entity, True)
        self._assert_valid_default_entity(result, self.default_prefix + "/core/" + random_name + "/v0.0.1")
        assert_that(result.is_published(), equal_to(True))

    def test_update(self):
        entity = self.repository.read(self.default_prefix, "core", "testschema", "v0.0.1")
        entity.data["description"] = "New description"
        entity = self.repository.update(entity)
        assert_that(entity.get_data("description"), not_none())
        entity.data["description"] = None
        self.repository.update(entity)

    def test_search_fulltext(self):
        self.test_create_and_publish()
        search = self.repository.list(full_text_query="schematest")
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

    def _create_and_publish_testschema(self):
        schema = self.repository.read("hbp", "core", "testschema", "v0.0.1")
        if schema is None:
            schema = self.repository.create(Schema.create_new("hbp", "core", "testschema", "v0.0.1", self.test_schema))
        if not schema.is_published():
            self.repository.publish(schema, True)

    def _create_testschema_v2(self):
        schema = self.repository.read("hbp", "core", "testschema", "v0.0.1")
        if schema is None:
            self.repository.create(Schema.create_new("hbp", "core", "testschema", "v0.0.1", self.test_schema))

    test_schema = {
        "@id": "http://nexus.example.com/v0/schemas/hbp/core/testschema/v0.0.1",
        "@type": "owl:Ontology",
        "@context": {
            "maxCount": {
                "@id": "sh:maxCount",
                "@type": "xsd:integer"
            },
            "minCount": {
                "@id": "sh:minCount",
                "@type": "xsd:integer"
            },
            "datatype": {
                "@id": "sh:datatype",
                "@type": "@id"
            },
            "name": "sh:name",
            "path": {
                "@id": "sh:path",
                "@type": "@id"
            },
            "nodeKind": {
                "@id": "node:Kind",
                "@type": "@id"
            },
            "description": "sh:description",
            "class": {
                "@id": "sh:class",
                "@type": "@id"
            },
            "property": {
                "@id": "sh:property",
                "@type": "@id"
            },
            "isDefinedBy": {
                "@id": "rdfs:isDefinedBy",
                "@type": "@id"
            },
            "targetClass": {
                "@id": "sh:targetClass",
                "@type": "@id"
            },
            "targetObjectOf": {
                "@id": "sh:targetObjectOf",
                "@type": "@id"
            },
            "node": {
                "@id": "sh:node",
                "@type": "@id"
            },
            "rest": {
                "@id": "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest",
                "@type": "@id"
            },
            "first": "http://www.w3.org/1999/02/22-rdf-syntax-ns#first",
            "in": {
                "@id": "sh:in",
                "@type": "@id"
            },
            "schema": "http://schema.org/",
            "this": "http://nexus.example.com/v0/vocab/hbp/core/testschema/v0.0.1/shape/",
            "hbp": "http://nexus.example.com/v0/vocab/hbp/core/testschema/",
            "sh": "http://www.w3.org/ns/shacl#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "shapes": {
                "@reverse": "rdfs:isDefinedBy",
                "@type": "@id"
            }
        },
        "shapes": [
            {
                "@id": "hbp:SchemaTestShape",
                "@type": "sh:NodeShape",
                "property": [
                    {
                        "description": "Hello World",
                        "path": "hbp:hello_world",
                        "maxCount": 1,
                        "datatype": "xsd:string",
                        "name": "hello world"
                    }
                ],
                "targetClass": "hbp:SchemaTestEntity"
            }
        ]
    }
