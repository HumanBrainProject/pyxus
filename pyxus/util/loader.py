import fnmatch
import json
import os
import os.path
import pystache

from pyxus.client import NexusClient


class Loader(object):

    client = None

    def __init__(self, client=NexusClient()):
        self.client = client

    def recursive_find_matching(self, root_path, pattern):
        matches = []
        for root, dirnames, filenames in os.walk(root_path):
            for filename in fnmatch.filter(filenames, pattern):
                matches.append(os.path.join(root, filename))

        return matches

    def list_schemas(self, root_path):
        return self.recursive_find_matching(root_path, "*shacl.ttl.json")

    def list_instances(self, root_path):
        return self.recursive_find_matching(root_path, "*data.json")

    def upload_schemas(self, file_root_path):
        schemas = self.list_schemas(file_root_path)
        for s in schemas:
            self.client.create_schema(s)

    def get_this_schema_name(self, json):
        path_segments = json['@context']['this'].split(os.sep)
        return '/' + os.path.join(*path_segments[5:-2])

    def upload_schema(self, file_path, schema_path=None):
        """Create a new schema or revise an existing.
        Arguments:
        file_path -- path to the location of the schema.json
        SHACL file to upload.
        schema_path -- path of the schema to create or update.
        Ensure that you increase the version portion of the path
        in the case of an update following semantic versioning
        conventions. Argument takes the form:
        '/{organization}/{domain}/{schema}/{version}'
        Keyword arguments:
        api_root -- URL for the root of the API,
        default = util.DEFAULT_API_ROOT
        """
        with open(file_path) as x:
            schema_str_template = x.read()
            schema_str = pystache.render(schema_str_template,
                                         self.client.api_root_dict)
            schema_json = json.loads(schema_str)
            return self.client.create_schema(
                self.get_this_schema_name(schema_json),
                schema_str)

    def upload_orgs(self):
        orgs = [('hbp', 'The Human Brain Project Organization'),
                ('nexus', 'Nexus Core'),
                ('bbp', 'The Blue Brain Project Organization')]

        for (name, desc) in orgs:
            self.client.create_org(name, desc)

    def upload_domains(self):
        domains = [('hbp', 'core', 'The HBP Core Domain'),
                   ('nexus', 'core', 'The Nexus Core Domain'),
                   ('nexus', 'schemaorg',
                    'The Nexus schemaorg domain based on the \
schema.org SHACL schemas'),
                   ('nexus', 'prov',
                    'The Nexus schemaorg domain based on the \
W3C PROV data model'),
                   ('bbp', 'core', 'The BBP Core Domain')]

        for (org, dom, desc) in domains:
            self.client.create_domain(org, dom, desc)
