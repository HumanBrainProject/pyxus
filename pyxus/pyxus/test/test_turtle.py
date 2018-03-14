import logging
from unittest import TestCase

from pyxus.client import NexusClient
from pyxus.resources.entity import Schema, Instance, Organization, Domain
from pyxus.test import env_setup

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
        env_setup.load_env()
        logging.basicConfig(level=logging.DEBUG)
        self.client = NexusClient()

    def test_create_turtle_schema(self):
        schema = self.client.schemas.read("test", "core", "turtle", "v0.0.3")
        if schema is None:
            self.client.schemas.create(Schema.create_new("test", "core", "turtle", "v0.0.3", self.test_turtle_schema, is_turtle=True))

    def test_create_turtle_instance(self):
        organization = self.client.organizations.read("test")
        if organization is None:
            self.client.organizations.create(Organization.create_new("test", "An organization for tests"))
        domain = self.client.domains.read("test", "core")
        if domain is None:
            self.client.domains.create(Domain.create_new("test", "core", "A domain for tests"))
        schema = self.client.schemas.read("test", "core", "turtle", "v0.0.4")
        if schema is None:
            schema = self.client.schemas.create(Schema.create_new("test", "core", "turtle", "v0.0.4", self.test_turtle_schema, is_turtle=True))
        if not schema.is_published():
            self.client.schemas.publish(schema, True)
        instance = self.client.instances.create(Instance.create_new("test", "core", "turtle", "v0.0.4", self.test_turtle_instance, is_turtle=True))
        instance = self.client.instances.read(instance.get_organization(), instance.get_domain(), instance.get_schema(), instance.get_version(), instance.get_id())
        print instance