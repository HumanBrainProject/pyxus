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

from setuptools import setup

if os.path.exists("../README.md"):
    try:
        import pypandoc
        long_description = pypandoc.convert('../README.md', 'rst')
    except(IOError, ImportError):
        long_description = open('../README.md').read()
else:
    long_description = "Pyxus is a python library for accessing and managing the nexus knowledge graph."

setup(
    name='pyxus',
    version='0.5.1',
    packages=['pyxus', 'pyxus.resources', 'pyxus.utils'],
    install_requires = ['pyld', 'rdflib', 'jinja2', 'openid_http_client', 'rdflib-jsonld'],
    author='HumanBrainProject',
    scripts=['manage.py'],
    author_email = 'platform@humanbrainproject.eu',
    keywords = ['pyxus', 'nexus'],
    classifiers = [],
    url = 'https://github.com/HumanBrainProject/pyxus',
    download_url = 'https://github.com/HumanBrainProject/pyxus/archive/master.zip',
    long_description = long_description
)
