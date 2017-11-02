import logging
import json
from abc import abstractmethod

from requests.exceptions import HTTPError

from pyxus.utils.exception import NexusException


class Resource(object):

    def __init__(self, http_client):
        self.http_client = http_client

    @staticmethod
    def get_revision(schema):
        if schema is None:
            raise NexusException(None, "Revision was not found")
        return schema.read("rev")

    @staticmethod
    def _build_instance_path(organization, domain, name, version, id):
        return "{}/{}/{}/{}/{}".format(organization, domain, name, version, id)

    @staticmethod
    def _build_schema_path(schema_organization, schema_domain, schema_name, schema_version):
        return "{}/{}/{}/{}".format(schema_organization, schema_domain, schema_name, schema_version)

    @staticmethod
    def build_schema_path_from_schema_data(schema_data):
        return Resource._build_schema_path(schema_data.organization, schema_data.domain, schema_data.schema_name, schema_data.version)
