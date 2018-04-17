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
import json
from unittest import TestCase

#   limitations under the License.
from mock.mock import MagicMock

from pyxus.utils.data_upload_utils import DataUploadUtils


class TestDataUploadUtils(TestCase):

    def test___resolve_entities(self):
        data_upload_utils = DataUploadUtils(None)
        data_upload_utils.resolve_identifier = MagicMock(return_value="foo")
        payload = {"@context": {"schema": "http://schema.org/", "test": "http://test.org#"}, "@type": ["test:Test"], "schema:identifier": "testIdentifier",
                   "test:relationA": "{{resolve /test/core/test/v0.0.1/?filter={\"op\":\"eq\",\"path\":\"http://schema.org/identifier\", \"value\":\"bar\"}}}",
                   "test:relationB": "{{resolve /test/core/test/v0.0.1/?filter={\"op\":\"eq\",\"path\":\"http://schema.org/identifier\", \"value\":\"bar\"}}}",
                   "test:xyz": "bar"}

        expected = {"schema:identifier": "testIdentifier", "test:relationA": {"@id": "foo"}, "test:relationB": {"@id": "foo"}, "@context": {"test": "http://test.org#", "schema": "http://schema.org/"}, "@type": ["test:Test"], "test:xyz": "bar"}
        result = data_upload_utils.resolve_entities(json.dumps(payload), False)
        self.assertEqual(json.dumps(expected), json.dumps(json.loads(result)))
