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


import json
import os

import requests

from pyxus.client import ENV_VAR_NEXUS_NAMESPACE

ENV_VAR_BLAZEGRAPH = "BLAZEGRAPH_ENDPOINT"
XSD_URI = "http://www.w3.org/2001/XMLSchema#"


class BlazegraphClient(object):
    """
    Client to access Blazegraph SPARQL API
    """

    def __init__(self, blazegraph_endpoint=None, nexus_namespace=None):
        if blazegraph_endpoint is None and ENV_VAR_BLAZEGRAPH in os.environ:
            self.BLAZEGRAPH_ENDPOINT = os.environ.get(ENV_VAR_BLAZEGRAPH)
        else:
            self.BLAZEGRAPH_ENDPOINT = blazegraph_endpoint
        if nexus_namespace is None and ENV_VAR_NEXUS_NAMESPACE in os.environ:
            self.NEXUS_NAMESPACE = os.environ.get(ENV_VAR_NEXUS_NAMESPACE)
        else:
            self.NEXUS_NAMESPACE = nexus_namespace

        if self.BLAZEGRAPH_ENDPOINT is None:
            raise ValueError("The Blazegraph endpoint is not set!")
        if self.NEXUS_NAMESPACE is None:
            raise ValueError("The Nexus namespace is not set!")

    def query(self, query, raw=False):
        """
        Send a query to blazegraph
        :param query: the query
        :param raw: true if the result should be returned raw. False if the result should be JSON
        :return: the result from blazegraph
        """
        query = {'query': query}
        response = requests.post("{}/{}".format(self.BLAZEGRAPH_ENDPOINT, "bigdata/namespace/kg/sparql"), data=query,
                                 headers={"Accept": "application/sparql-results+json", "Content-Type": "application/x-www-form-urlencoded"})
        if response.status_code == 200:
            if raw:
                return response.content
            else:
                content = json.loads(response.content)
                if content:
                    return content["results"]["bindings"]
                return None
        return None

    def _get_vocab(self):
        return "{}/vocabs".format(self.NEXUS_NAMESPACE)

    def _get_uuid_predicate(self):
        return "{}/nexus/core/terms/v0.1.0/uuid".format(self._get_vocab())

    def get_reverse_relations(self, uuid):
        """
        Will return a list of entities related to the entity uuid
        :param uuid: The entity
        :return: a list of all the relations to the entity
        """
        query = "prefix xsd: <{xsd}>\n" \
                "SELECT ?rel" \
                " WHERE {{" \
                "?s <{uuid_pred}> \"{id}\"^^xsd:string. " \
                "?rel ?p ?s" \
                "}}".format(xsd=XSD_URI, uuid_pred=self._get_uuid_predicate(), id=uuid)
        response = self.query(query)
        result = [i.get("rel").get("value") for i in response]
        return result
