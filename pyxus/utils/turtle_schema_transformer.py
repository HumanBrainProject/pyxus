import json

from rdflib.graph import Graph

def transform_turtle_to_jsonld(turtle):
    g = Graph().parse(data=turtle, format='turtle')
    content_jsonld = g.serialize(format='json-ld', indent=4)
    return json.loads(content_jsonld)

def transform_turtle_to_jsonld_schema(turtle_shapes):
    return _wrap(transform_turtle_to_jsonld(turtle_shapes))

def _wrap(jsonld):
    return {
        "@type": "owl:Ontology",
        "@context": {
            "owl": "http://www.w3.org/2002/07/owl#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "isDefinedBy": {
                "@id": "rdfs:isDefinedBy",
                "@type": "@id"
            },
            "shapes": {
                "@reverse": "rdfs:isDefinedBy",
                "@type": "@id"
            }
        },
        "shapes": jsonld
    }
