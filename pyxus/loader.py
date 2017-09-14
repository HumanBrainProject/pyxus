
from attrdict import AttrDict

import fnmatch
import json
import os
import os.path
import requests
import pystache

import pyxus.util as util
from pyxus.client import NexusClient

DEFAULT_CLIENT = NexusClient()

def recursive_find_matching(root_path, pattern):
    matches = []
    for root, dirnames, filenames in os.walk(root_path):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))

    return matches


def list_schemas(root_path):
    return recursive_find_matching(root_path, "*shacl.ttl.json")


def list_instances(root_path):
    return recursive_find_matching(root_path, "*data.json")


def upload_schemas(file_root_path, client=DEFAULT_CLIENT):
    schemas = list_schemas(file_root_path)


def get_this_schema_name(json):
    path_segments = json['@context']['this'].split(os.sep)
    return '/' + os.path.join(*path_segments[5:-2])


def upload_schema(file_path, schema_path = None, client=DEFAULT_CLIENT):
    """Create a new schema or revise an existing.

    Arguments:
    file_path -- path to the location of the schema.json SHACL file to upload.
    schema_path -- path of the schema to create or update. Ensure that you increase the version portion of the path in the case of an update following semantic versioning conventions. Argument takes the form '/{organization}/{domain}/{schema}/{version}'
    Keyword arguments:
    api_root -- URL for the root of the API, default = util.DEFAULT_API_ROOT
    """
    with open(file_path) as x: schema_str_template = x.read()
    schema_str = pystache.render(schema_str_template, client.api_root_dict)
    schema_json = json.loads(schema_str)
    return client.put_schema(get_this_schema_name(schema_json), schema_str)


def load_instance(data_file = None, data_str = None):
    """Create a new schema or revise an existing.

    Arguments:
    Keyword arguments:
    data_file -- path or file for the location of the .json instance in JSON-LD format.
    data_str -- string data payload
    NOTE: only one of data_file or data_str should be specified
    """
    if data_file is not None and data_str is not None:
        raise ValueError('At most one of data_file or data_str can be specified')
    if data_file is None and data_str is None:
        raise ValueError('At least one of data_file or data_str must be specified')

    j = None
    if data_file is not None:
        if isinstance(data_file, file):
            j = json.load(data_file)
        elif isinstance(data_file, str):
            j = json.load(open(data_file))
        else:
            raise ValueError('data_file must be of type file or string.')
    else:
        j = json.loads(data_str)

    return j


def get_instance(resultId = None, searchResult = None):
    """Create a new schema or revise an existing.

    Arguments:
    Keyword arguments:
    resultId -- URI to the instance we want to retrieve and decode
    searchResult -- SearchResult object which corresponds to the object we want to fetch used
    Returns:
    a dict representing the instance using JSON-LD conventions for keys and values
    """

    # if resultId and searchResult?
    if not(bool(resultId is None) ^ bool(searchResult is None)) :
        raise ValueError('only one of resultId and searchResult arguments can be specified')

    if searchResult is not None:
        resultId = searchResult.resultId

    req = requests.get(resultId, headers = util.JSON_CONTENT)
    return load_instance(data_str = req.content)


def upload_orgs(client=DEFAULT_CLIENT):
    orgs = [('hbp', 'The HBP Organization'),
            ('nexus', 'Nexus Core')
            ('bbp', 'The BBP Organization')]

    for (name, desc) in orgs:
        client.put_org(name, desc)


def upload_domains(client=DEFAULT_CLIENT):
    domains = [('hbp','core','The HBP Core Domain'),
            ('bbp', 'core', 'The BBP Core Domain')]

    for (org, dom, desc) in domains:
        client.put_domain(org, dom, desc)
