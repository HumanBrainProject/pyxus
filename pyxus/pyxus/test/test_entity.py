#  Copyright 2018 - 2021 Swiss Federal Institute of Technology Lausanne (EPFL)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0.
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  This open source software code was developed in part or in whole in the
#  Human Brain Project, funded from the European Union's Horizon 2020
#  Framework Programme for Research and Innovation under
#  Specific Grant Agreements No. 720270, No. 785907, and No. 945539
#  (Human Brain Project SGA1, SGA2 and SGA3).
#



import logging
import os
from unittest import TestCase

from pyxus.resources.constants import ENV_VAR_HASHCODE_NAMESPACE, ENV_VAR_NEXUS_NAMESPACE
from pyxus.resources.entity import Entity, Schema
from pyxus.test import env_setup


class TestEntity(TestCase):

    def setUp(self):
        env_setup.load_env()
        logging.basicConfig(level=logging.DEBUG)

    def test_extract_id_from_url(self):
        result = Entity.extract_id_from_url(
            "http://kg:8080/v0/schemas/hbp/core/celloptimization/v0.0.1", Schema.path)
        self.assertEqual(result, "hbp/core/celloptimization/v0.0.1")

    def test_extract_id_from_url_with_param(self):
        result = Entity.extract_id_from_url(
            "http://kg:8080/v0/schemas/hbp/core/celloptimization/v0.0.1?hello_world", Schema.path)
        self.assertEqual(result, "hbp/core/celloptimization/v0.0.1")

    def test_extract_id_from_url_with_anchor(self):
        result = Entity.extract_id_from_url(
            "http://kg:8080/v0/schemas/hbp/core/celloptimization/v0.0.1#hello_world", Schema.path)
        self.assertEqual(result, "hbp/core/celloptimization/v0.0.1")

    def test_extract_id_from_url_with_slash_at_the_end(self):
        result = Entity.extract_id_from_url(
            "http://kg:8080/v0/schemas/hbp/core/celloptimization/v0.0.1/", Schema.path)
        self.assertEqual(result, "hbp/core/celloptimization/v0.0.1")

    def test_extract_id_from_url_with_wrong_entity(self):
        with self.assertRaises(ValueError):
            Entity.extract_id_from_url(
                "http://kg:8080/v0/organizations/hbp/core/celloptimization/v0.0.1", Schema.path)

    def test_expand(self):
        data = {
            "@context": [{
                "hbp": "http://localhost:8080/vocab/hbp/core/celloptimization/",
            }],
            "imports": [
                "{{scheme}}://{{host}}/{{prefix}}/schemas/nexus/core/datadownload/v1.0.0"
            ],
            "hbp:contributors": "Homer Simpson"
        }
        qualified_data = Entity.fully_qualify(data)
        expected_data = {
            'http://localhost:8080/vocab/hbp/core/celloptimization/contributors': 'Homer Simpson'}

        self.assertEqual(qualified_data, expected_data)

    def test_do_get_checksum(self):
        data1 = {
            "foo": "bar"
        }
        os.environ[ENV_VAR_HASHCODE_NAMESPACE] = "bar"
        os.environ[ENV_VAR_NEXUS_NAMESPACE] = "foo"
        data2 = {
            "bar": "bar"
        }
        checksum1 = Entity.do_get_checksum(data1)
        checksum2 = Entity.do_get_checksum(data2)

        self.assertEqual(checksum1, checksum2)