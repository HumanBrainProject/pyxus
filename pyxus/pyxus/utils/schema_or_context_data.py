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


import re
import os


class SchemaOrContextData(object):
    revision = None

    @staticmethod
    def _recursively_check_for_this(json_element):
        if type(json_element) is list:
            for item in json_element:
                if type(item) is dict:
                    result = SchemaOrContextData._recursively_check_for_this(item)
                    if result is not None:
                        return result
        elif type(json_element) is dict and 'this' in json_element:
            return json_element['this']
        return None

    @classmethod
    def by_filepath(cls, filepath, content):
        dirname = os.path.dirname(filepath)
        split = os.path.split(dirname)
        try:
            version = re.search("v\d*\.\d*\.\d*", os.path.basename(filepath)).group(0)
        except:
            version=split[1]
            split = os.path.split(split[0])
        name=split[1]
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
