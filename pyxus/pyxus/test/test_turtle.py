#   Copyright (c) 2018, EPFL/Human Brain Project PCO
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging
from unittest import TestCase
from deepdiff import DeepDiff

from pyxus.test import utils
from pyxus.utils.turtle_schema_transformer import transform_turtle_to_jsonld_schema, transform_turtle_to_jsonld


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
                           "  foaf:name \"Bar\";  ."

    expected_jsonld_schema = {
        'shapes':
            [{
                u'http://www.w3.org/ns/shacl#maxCount': [{u'@value': 1}],
                u'@id': u'_:ub1bL0C255',
                u'http://www.w3.org/ns/shacl#path': [{u'@id': u'http://xmlns.com/foaf/0.1/name'}],
                u'http://www.w3.org/ns/shacl#minCount': [{u'@value': 1}],
                u'http://www.w3.org/ns/shacl#datatype': [{u'@id': u'http://www.w3.org/2001/XMLSchema#string'}]
            }, {
                u'http://www.w3.org/ns/shacl#property': [{u'@id': u'_:ub1bL0C255'}],
                u'http://www.w3.org/ns/shacl#targetClass': [{u'@id': u'http://xmlns.com/foaf/0.1/Person'}],
                u'@id': u'http://foaf_sh.com/PersonShape', u'@type': [u'http://www.w3.org/ns/shacl#NodeShape']}],
        '@context': {
            'shapes': {
                '@reverse': 'rdfs:isDefinedBy',
                '@type': '@id'},
            'owl': 'http://www.w3.org/2002/07/owl#',
            'isDefinedBy': {
                '@id': 'rdfs:isDefinedBy',
                '@type': '@id'},
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'},
        '@type': 'owl:Ontology'}

    json_schema_id = '_:ub1bL0C255'
    expected_jsonld_instance = [
        {u'http://xmlns.com/foaf/0.1/name': [{u'@value': u'Bar'}],
         u'@id': u'http://foaf_sh.com/Foo',
         u'@type': [u'http://xmlns.com/foaf/0.1/Person']}]

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    @staticmethod
    def __ignore_id(value_to_ignore, deepdiff_dict):
        return value_to_ignore in deepdiff_dict['new_value'] or value_to_ignore in deepdiff_dict['old_value']

    def test_create_turtle_schema(self):
        jsonld_schema = transform_turtle_to_jsonld_schema(self.test_turtle_schema)
        res = DeepDiff(utils.ordered(jsonld_schema), utils.ordered(self.expected_jsonld_schema))
        if res['values_changed']:
            assert all(self.__ignore_id(self.json_schema_id, value)for key, value in res['values_changed'].iteritems())
        assert True

    def test_create_turtle_instance(self):
        jsonld_instance = transform_turtle_to_jsonld(self.test_turtle_instance)
        assert cmp(jsonld_instance, self.expected_jsonld_instance) == 0
