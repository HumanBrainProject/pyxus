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

from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('../README.md', 'rst')
except(IOError, ImportError):
    long_description = open('../README.md').read()

setup(
    name='pyxus',
    version='0.2.0',
    packages=['pyxus', 'pyxus.resources', 'pyxus.utils'],
    install_requires = ['pyld', 'rdflib', 'pystache', 'openid_http_client', 'rdflib-jsonld'],
    author='HumanBrainProject',
    scripts=['manage.py'],
    author_email = 'platform@humanbrainproject.eu',
    keywords = ['pyxus', 'nexus'],
    classifiers = [],
    url = 'https://github.com/HumanBrainProject/pyxus',
    download_url = 'https://github.com/HumanBrainProject/pyxus/archive/master.zip',
    long_description = long_description
)
