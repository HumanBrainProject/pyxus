
#import rdflib
#import rdflib_jsonld

#from rdflib import Graph, plugin
#from rdflib.serializer import Serializer


from rdflib.plugin import register, Parser, Serializer
register('json-ld', Parser, 'rdflib_jsonld.parser', 'JsonLDParser')
register('json-ld', Serializer, 'rdflib_jsonld.serializer', 'JsonLDSerializer')

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF

def load_jsonld(source):
    return Graph().parse(source=source, format='json-ld')

def load_ttl(source):
    return Graph().parse(source=source, format='turtle')

def pretty_jsonld(g, context=None):
    if context:
        return g.serialize(format='json-ld', indent=4, context=context)
    else:
        return g.serialize(format='json-ld', indent=4)

#This is a WIP, needs to be recursive across triples
def to_dict(g):
    l = g.triples((None,RDF.type,None))
    ll = list(l)
    root_types = []
    for (s,p,o) in ll:
        if len(list(g.subjects((None,None,None))):
               root_types += s
