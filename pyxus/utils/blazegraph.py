import json
import os

import requests

from pyxus.client import ENV_VAR_NEXUS_NAMESPACE

ENV_VAR_BLAZEGRAPH = "BLAZEGRAPH_ENDPOINT"
XSD_URI="http://www.w3.org/2001/XMLSchema#"

class BlazegraphClient(object):
    """
    Client to access Blazegraph SPARQL API
    """
    def __init__(self, blazegraph_endpoint=None, nexus_namespace=None):
        self.BLAZEGRAPH_ENDPOINT = os.environ.get(ENV_VAR_BLAZEGRAPH) if blazegraph_endpoint is None and ENV_VAR_BLAZEGRAPH in os.environ else blazegraph_endpoint
        self.NEXUS_NAMESPACE = os.environ.get(ENV_VAR_NEXUS_NAMESPACE) if nexus_namespace is None and ENV_VAR_NEXUS_NAMESPACE in os.environ else nexus_namespace
        if self.BLAZEGRAPH_ENDPOINT is None:
            raise ValueError("The Blazegraph endpoint is not set!")
        if self.NEXUS_NAMESPACE is None:
            raise ValueError("The Nexus namespace is not set!")

    def query(self, query, raw=False, timeout=30):
        """
        Send a query to blazegraph
        :param query: the query
        :param raw: true if the result should be returned raw. False if the result should be JSON
        :return: the result from blazegraph
        """
        query = {'query': query}
        response = requests.post("{}/{}".format(self.BLAZEGRAPH_ENDPOINT, "bigdata/namespace/kg/sparql"), data=query, headers={"Accept": "application/sparql-results+json", "Content-Type": "application/x-www-form-urlencoded"}, timeout=timeout)
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
        return "{}/vocabs".format(self.NEXUS_NAMESPACE)

    def _get_uuid_predicate(self):
        return "{}/nexus/core/terms/v0.1.0/uuid".format(self._get_vocab())

    def get_reverse_relations(self, uuid, timeout=30):
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
        response = self.query(query, timeout=timeout)
        result = [i.get("rel").get("value") for i in response]
        return result