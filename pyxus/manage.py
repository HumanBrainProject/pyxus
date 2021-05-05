#!/usr/bin/env python
# pylint: disable=missing-docstring

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

import os
import sys

if __name__ == "__main__":

    # load the content of .env in the current environement
    env_filename = '.env2'

    if 'test' in sys.argv:
        env_filename = '.env.sample'
    if os.path.exists(env_filename):
        with open(env_filename) as f:
            env = dict([line.split('=', 1) for line in f.readlines()])
            for k in env:
                os.environ.setdefault(k, env[k].strip())
    @staticmethod
    def setUp():
        env_setup.load_env()

    @staticmethod
    def test__transform_url_to_defined_endpoint():
        client = HttpClient("http://foo", "v0")
        result = client.transform_url_to_defined_endpoint("https://nexus-dev.humanbrainproject.org/v0/data/something")
        print result
        assert result == "http://foo/v0/data/something"
