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



import re
import os


class SchemaOrContextData(object):
    revision = None

    @staticmethod
    def _recursively_check_for_this(json_element):
        if isinstance(json_element, list):
            for item in json_element:
                if isinstance(item, dict):
                    result = SchemaOrContextData._recursively_check_for_this(item)
                    if result is not None:
                        return result
        elif isinstance(json_element, dict) and 'this' in json_element:
            return json_element['this']
        return None

    @classmethod
    def by_filepath(cls, filepath, content):
        dirname = os.path.dirname(filepath)
        split = os.path.split(dirname)
        try:
            version_in_filename = re.search(r"v\d*\.\d*\.\d*", os.path.basename(filepath))
            if version_in_filename:
                version = version_in_filename.group(0)
            else:
                version = split[1]
                split = os.path.split(split[0])
        except re.error:
            version = split[1]
            split = os.path.split(split[0])
        name = split[1]
        split = os.path.split(split[0])
        domain = split[1]
        split = os.path.split(split[0])
        organization = split[1]
        return SchemaOrContextData(organization, domain, name, version, content)

    def __init__(self, organization, domain, name, version, content):
        self.organization = self._normalize_identifier(organization)
        self.domain = self._normalize_identifier(domain)
        self.name = self._normalize_identifier(name)
        self.version = self._normalize_identifier(version)
        self.content = content

    @staticmethod
    def _normalize_identifier(identifier):
        return re.sub('[/#]', '', identifier)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
