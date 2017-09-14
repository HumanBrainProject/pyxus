
#import rdflib
#import rdflib_jsonld

#from rdflib import Graph, plugin
#from rdflib.serializer import Serializer

DEFAULT_SCHEME = "http"
DEFAULT_HOST = "localhost:8080"
DEFAULT_PREFIX = "v0"
DEFAULT_API_ROOT = "{}://{}/{}".format(DEFAULT_SCHEME, DEFAULT_HOST, DEFAULT_PREFIX)
DEFAULT_API_ROOT_DICT = {
    'scheme' : DEFAULT_SCHEME,
    'host' : DEFAULT_HOST,
    'prefix' : DEFAULT_PREFIX
}

JSON_CONTENT = { "Content-type" : "application/json" }
