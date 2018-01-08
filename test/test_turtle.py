import logging
from unittest import TestCase

import pyxus.config as conf
from pyxus.resources.entity import Schema, Instance
from pyxus.resources.repository import SchemaRepository, InstanceRepository
from pyxus.utils.http_client import HttpClient


class TestSchemaRepository(TestCase):

    test_turtle_schema = "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> ." \
                         "@prefix sh: <http://www.w3.org/ns/shacl#> ." \
                      "@prefix foaf: <http://xmlns.com/foaf/0.1/> ." \
                      "@prefix foaf_sh: <http://foaf_sh.com/> ." \
                      "" \
                      "foaf_sh:PersonShape" \
                      "	a sh:NodeShape ;" \
                      "	sh:targetClass foaf:Person;" \
                      "	sh:property [" \
                      "     sh:path foaf:name;" \
                      "		     sh:minCount 1 ;" \
                      "		     sh:maxCount 1 ;" \
                      "		     sh:datatype xsd:string;" \
                      "] ."

    test_turtle_instance = "@prefix foaf: <http://xmlns.com/foaf/0.1/> ." \
                           "@prefix foaf_sh: <http://foaf_sh.com/> ." \
                           "foaf_sh:Foo" \
                           "  a foaf:Person ;" \
                           "  foaf:name \"Bar\";  ." \


    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.schema_repository = SchemaRepository(HttpClient(conf.NEXUS_ENV_LOCALHOST))
        self.instance_repository = InstanceRepository(HttpClient(conf.NEXUS_ENV_LOCALHOST))

    def test_create_turtle_schema(self):
        schema = self.schema_repository.read("test", "core", "turtle", "v0.0.3")
        if schema is None:
            self.schema_repository.create(Schema.create_new("test", "core", "turtle", "v0.0.3", self.test_turtle_schema, is_turtle=True))

    def test_create_turtle_instance(self):
        schema = self.schema_repository.read("test", "core", "turtle", "v0.0.4")
        if schema is None:
            schema = self.schema_repository.create(Schema.create_new("test", "core", "turtle", "v0.0.4", self.test_turtle_schema, is_turtle=True))
        if not schema.is_published():
            self.schema_repository.publish(schema, True)
        instance = self.instance_repository.create(Instance.create_new("test", "core", "turtle", "v0.0.4", self.test_turtle_instance, is_turtle=True))
        instance = self.instance_repository.read(instance.get_organization(), instance.get_domain(), instance.get_schema(), instance.get_version(), instance.get_id())
        print instance