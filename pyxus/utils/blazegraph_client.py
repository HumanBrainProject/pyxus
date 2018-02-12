import json
import os

import requests

from pyxus.client import ENV_VAR_NEXUS_NAMESPACE

ENV_VAR_BLAZEGRAPH = "BLAZEGRAPH_ENDPOINT"
XSD_URI="http://www.w3.org/2001/XMLSchema#"

class BlazegraphClient(object):

    def __init__(self, blazegraph_endpoint=None, nexus_namespace=None):
        self.BLAZEGRAPH_ENDPOINT = os.environ.get(ENV_VAR_BLAZEGRAPH) if blazegraph_endpoint is None and ENV_VAR_BLAZEGRAPH in os.environ else blazegraph_endpoint
        self.NEXUS_NAMESPACE = os.environ.get(ENV_VAR_NEXUS_NAMESPACE) if nexus_namespace is None and ENV_VAR_NEXUS_NAMESPACE in os.environ else nexus_namespace
        if self.BLAZEGRAPH_ENDPOINT is None:
            raise ValueError("The Blazegraph endpoint is not set!")
        if self.NEXUS_NAMESPACE is None:
            raise ValueError("The Nexus namespace is not set!")

    def query(self, query, raw=False):
        query = {'query': query}
        response = requests.post(self.BLAZEGRAPH_ENDPOINT, data=query, headers={"Accept": "application/sparql-results+json", "Content-Type": "application/x-www-form-urlencoded"})
        if response.status_code == 200:
            if raw:
                return response.content
            else:
                content = json.loads(response.content)
                if content:
                    return content["results"]["bindings"]
                else:
                    return None
        return None

    def _get_vocab(self):
        return "{}/voc".format(self.NEXUS_NAMESPACE)

    def _get_uuid_predicate(self):
        return "{}/nexus/core/uuid".format(self._get_vocab())

    def get_reverse_relations(self, uuid):
        query = "prefix xsd: <{xsd}>\n" \
                "SELECT ?rel" \
                " WHERE {{" \
                "?s <{uuid_pred}> \"{id}\"^^xsd:string. " \
                "?rel ?p ?s" \
                "}}".format(xsd=XSD_URI, uuid_pred=self._get_uuid_predicate(), id=uuid)
        response = self.query(query)
        result = [i.get("rel").get("value") for i in response]
        return result