import logging
from unittest import TestCase

from pyxus import config
from pyxus.resources.entity import Instance
from pyxus.resources.repository import InstanceRepository
from pyxus.utils.http_client import HttpClient


class TestEntity(TestCase):

    origin_content = {
        "@context": {
            "schema": "http://schema.org/",
            "shape": "http://shapes.org/"
        },
        "@type": [
            "shape:Person"
        ],
        "schema:identifier": "a",
        "schema:name": "foo",
        "schema:myvalue": "barfoo"
    }

    target_content = {
        "@context": {
            "schema": "http://schema.org/",
            "shape": "http://shapes.org/"
        },
        "@type": [
            "shape:Person"
        ],
        "schema:identifier": "b",
        "schema:name": "bar",
        "schema:somethingelse": "foobar"
    }

    referencing_content= {
        "@context": {
            "schema": "http://schema.org/",
            "shape": "http://shapes.org/"
        },
        "@type": [
            "shape:Dataset"
        ],
        "schema:identifier": "adata",
        "schema:name": "foodata",
        "schema:person": {
            "@id": "a"
        }
    }


    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.repository = InstanceRepository(HttpClient(config.NEXUS_ENV_HBP_DEV))

    def test_merge_instances(self):
        origin = Instance.create_new("foo", "bar", "foobar", "v0.0.1", Instance.fully_qualify(self.origin_content))
        target = Instance.create_new("foo", "bar", "foobar", "v0.0.1", Instance.fully_qualify(self.target_content))
        ref = Instance.create_new("foo", "bar", "foobar", "v0.0.1", Instance.fully_qualify(self.referencing_content))
        for key in origin.data:
            self.add_if_not_exists(origin.data, target.data, key)
        self.merge_key(origin.data, target.data, "http://schema.org/identifier")
        for ref_instance in [ref]:
            self.update_reference(ref_instance.data, "a", "b")
        print target
        print ref
