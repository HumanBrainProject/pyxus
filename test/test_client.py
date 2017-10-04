
# encoding: utf-8

from pyxus.client import NexusClient

import glob
import json
import logging
import unittest
import pyxus.config as conf
import pyxus.util as u

from hamcrest import (assert_that, instance_of, has_properties, not_none)

LOGGER = logging.getLogger(__name__)

TEST_INSTANCE_FILE = """
{
  "@context": {
    "@vocab": "http://schema.org/",
    "@base": "https://bbp-nexus.epfl.ch/data/bbp/contributing/organization/v1.0.0/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "prov": "http://www.w3.org/ns/prov#",
    "Organization": "http://schema.org/Organization",
    "PostalAddress": "http://schema.org/PostalAddress"
  },
  "@type": "Organization",
  "@id": "5cb48794-1af3-4dcc-9271-540bc82361c2",
  "name": "Blue Brain Project",
  "address": {
    "@type": "PostalAddress",
    "@id": "5cb48794-1af8-4dec-9271-540bc82361c2",
    "streetAddress": {
      "@type": "xsd:string",
      "@value": "Chemin des Mines 9"
    },
    "postalCode": {
      "@type": "xsd:string",
      "@value": "1202"
    },
    "addressLocality": {
      "@type": "xsd:string",
      "@value": "Campus Biotech, Geneva"
    },
    "addressCountry": {
      "@type": "xsd:string",
      "@value": "Switzerland"
    },
    "telephone": {
      "@type": "xsd:string",
      "@value": "+41 21 693 76 60"
    }
  },
  "parentOrganization": {
    "@type": "Organization",
    "@id": "5cb48794-1af3-4dcc-921-540bc82361c2",
    "name": "Ecole Polytechnique Fédérale de Lausanne",
    "address": {
      "@type": "xsd:string",
      "@value": "Route Cantonale, 1015 Lausanne"
    }
  }
}
"""

TEST_INSTANCE_READ="""
{
    "deprecated": false,
    "@id": "https://bbp-nexus.epfl.ch/dev/v0/data/bbp/experiment/emptysubjectcollection/v0.1.0/bd8e5e40-a2d7-4d1f-bf98-adf5edd1333a",
    "rev": 1,
    "@context": {
        "@base": "https://bbp-nexus.epfl.ch/dev/v0/voc/experiment/core/",
        "@vocab": "https://bbp-nexus.epfl.ch/dev/v0/voc/experiment/core/",
        "age": "https://bbp-nexus.epfl.ch/dev/v0/voc/experiment/core/age",
        "bbpexp": "https://bbp-nexus.epfl.ch/dev/v0/voc/experiment/core/",
        "description": "http://schema.org/description",
        "label": "http://www.w3.org/2000/01/rdf-schema#label",
        "name": "http://schema.org/name",
        "period": "https://bbp-nexus.epfl.ch/dev/v0/voc/experiment/core/period",
        "providerId": "https://bbp-nexus.epfl.ch/dev/v0/voc/experiment/core/providerId",
        "species": "https://bbp-nexus.epfl.ch/dev/v0/voc/experiment/core/species",
        "strain": "https://bbp-nexus.epfl.ch/dev/v0/voc/experiment/core/strain",
        "unitCode": "http://schema.org/unitCode",
        "value": "http://schema.org/value",
        "size": "http://schema.org/size",
        "prov": "http://www.w3.org/ns/prov#"
    },
    "@type": "prov:EmptyCollection",
    "name": "Subjectcollection of Paxinos rat",
    "description": "collection of rat of Paxinos rat atlas",
    "size": 1,
    "species": {
        "@id": "http://purl.obolibrary.org/obo/NCBITaxon_10116",
        "label": "Rattus norvegicus"
    }
}"""

class TestClient(unittest.TestCase):

    client = {}

    def setUp(self):
        self.client['localhost'] = NexusClient(**conf.NEXUS_ENV_LOCALHOST)
        self.client['hbp_prod'] = NexusClient(**conf.NEXUS_ENV_HBP_PROD)
        self.client['hbp_dev'] = NexusClient(**conf.NEXUS_ENV_HBP_DEV)
        self.client['bbp_dev'] = NexusClient(**conf.NEXUS_ENV_BBP_DEV)

    def test_client_is_instantiable(self):
        for client in self.client.values():
            assert_that(client, not_none())

    def test_client_envs(self):
        #explicitly test that the endpoints match the expected value
        assert_that(self.client['localhost'].api_root, 'http://localhost:8080/v0')
        assert_that(self.client['hbp_prod'].api_root, 'https://nexus.humanbrainproject.eu/v0')
        assert_that(self.client['hbp_dev'].api_root, 'https://nexus-dev.humanbrainproject.eu/v0')
        assert_that(self.client['bbp_dev'].api_root, 'https://bbp-nexus.epfl.ch/dev/v0')

    def test_hbp_dev_create(self):
        pass

    def test_read_org(self):
        response = self.client['bbp_dev'].read_org('hbp')
        LOGGER.debug('response.status_code: %s', response.status_code)
        LOGGER.debug('response.content: %s', response.content)
        assert_that(response.ok)

    def test_load_instance_from_data_file(self):
        inst = self.client['bbp_dev'].load_instance(data_file = 'test/data/nexus_schemaorg_organization_data.json')
        LOGGER.debug('json file content:\n%s')
        assert(inst == json.loads(TEST_INSTANCE_FILE))

    def test_read_instance(self):
        inst = self.client['bbp_dev'].read_instance(resultId = 'https://bbp-nexus.epfl.ch/dev/v0/data/bbp/experiment/emptysubjectcollection/v0.1.0/bd8e5e40-a2d7-4d1f-bf98-adf5edd1333a')
        LOGGER.debug('json file content:\n%s')
        assert(inst == json.loads(TEST_INSTANCE_READ))

    def test_read_instance_not_equal(self):
        inst = self.client['bbp_dev'].read_instance(resultId = 'https://bbp-nexus.epfl.ch/dev/v0/data/bbp/experiment/emptysubjectcollection/v0.1.0/bd8e5e40-a2d7-4d1f-bf98-adf5edd1333a')
        LOGGER.debug('json file content:\n%s')
        assert(inst != json.loads(TEST_INSTANCE_FILE))

    def test_update(self):
        pass

    def test_delete(self):
        pass

if __name__ == '__main__':
    logging.basicConfig()

    # Level	Numeric value
    # CRITICAL   50
    # ERROR	 40
    # WARNING	 30
    # INFO	 20
    # DEBUG	 10
    # NOTSET	 0
    LOGGER.setLevel(20)

    unittest.main()
    # a = TestClient('test_parse')
    # a.test_client_construct()
    # a.test_client_is_instantiable()
    # a.test_client_envs()
