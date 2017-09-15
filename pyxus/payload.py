import json


JSON_CONTENT = { "Content-type" : "application/json" }


class NexusPayload(dict):
    """
    Simple wrapper for JSON-LD / SHACL data.
    """
    
    def __init__(self, *args, **kwargs):
        super(NexusPayload, self).__init__(*args, **kwargs)

    @property
    def content_mimetype(self):
        return JSON_CONTENT

    def __str__(self):
        return json.dumps(self)

    @classmethod
    def from_str(cls, jsonld):
        return cls(json.loads(jsonld))