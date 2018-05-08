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


import fnmatch
import json
import logging
import os
import os.path

from pyxus.utils.generic_data_upload_utils import GenericDataUploadUtils
from pyxus.utils.schema_or_context_data import SchemaOrContextData

LOGGER = logging.getLogger(__package__)


def recursive_find_matching(root_path, pattern):
    matches = []
    for root, _, filenames in os.walk(root_path):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))

    return matches


class DataUploadUtils(GenericDataUploadUtils):
    _client = None

    def create_schema_by_file(self, file_path, force_domain_creation=False, update_if_already_exists=False, publish=False):
        return self.__create_schema_or_context_by_file(self.create_schema, file_path, force_domain_creation, update_if_already_exists, publish)

    def create_context_by_file(self, file_path, force_domain_creation=False, update_if_already_exists=False, publish=False):
        return self.__create_schema_or_context_by_file(self.create_context, file_path, force_domain_creation, update_if_already_exists, publish)

    def __create_schema_or_context_by_file(self, creation_function, file_path,
                                           force_domain_creation=False, update_if_already_exists=False, publish=False):
        """Create a new schema or context or revise an existing.

        Arguments:
        creation_function -- the function to create the structure (either for context or schema)
        file_path -- path to the location of the schema/context
        force_domain_creation -- if the organization and domain declared as part of the schema/context shall be created automatically
        update_if_already_exists -- if an already existing schema/context shall be updated.
        publish -- if the created or updated schema/context shall be published immediately (required for instance generation)
        """
        with open(file_path) as x:
            file_content = x.read()
            file_content = self._process_content(file_content)
            raw_content = self.__fill_placeholders(file_content)
            content = json.loads(raw_content)
            schema_data = SchemaOrContextData.by_filepath(file_path, content)
            return creation_function(schema_data, force_domain_creation, update_if_already_exists, publish)

    def create_instance_by_file(self, file_path, fail_if_linked_instance_is_missing=True):
        """Create a new instance for the provided data

        Arguments:
            file_path -- path to the location of the file to be uploaded as instance
            fully_qualify -- if True, prefixes are resolved and the JSON-LD to be uploaded will be interpretable as JSON
                             (but with non-human-friendly, fully qualified keys)
        """
        with open(os.path.abspath(file_path)) as metadata_file:
            file_content = metadata_file.read()
            schema_data = SchemaOrContextData.by_filepath(file_path, None)
            self.create_instance(file_content, schema_data, fail_if_linked_instance_is_missing)

    @staticmethod
    def clear_all_checksums(path):
        for match in recursive_find_matching(path, "*.chksum"):
            os.remove(match)