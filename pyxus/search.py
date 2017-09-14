
import json
import requests

import pyxus.util as util

test_result = '''{u'resultId': u'https://nexus.humanbrainproject.eu/dev/v0/data/hbp/experiment/subject/v0.0.5/44adb543-e430-4600-b852-8a8e3b075679',
   u'score': 0.625,
   u'source': {u'@id': u'https://nexus.humanbrainproject.eu/dev/v0/data/hbp/experiment/subject/v0.0.5/44adb543-e430-4600-b852-8a8e3b075679',
    u'links': [{u'href': u'https://nexus.humanbrainproject.eu/dev/v0/data/hbp/experiment/subject/v0.0.5/44adb543-e430-4600-b852-8a8e3b075679',
      u'rel': u'self'},
     {u'href': u'https://nexus.humanbrainproject.eu/dev/v0/schemas/hbp/experiment/subject/v0.0.5',
      u'rel': u'schema'}]}}'''


class Search(object):
    @staticmethod
    def search(search, offset = 0, limit = 10, api_root = util.DEFAULT_API_ROOT):
        req = requests.get( '{}/data?q={}&offset={}&limit={}'.format(api_root, search, offset, limit), headers = util.JSON_CONTENT)
        #return req.content
        #return [r for r in json.loads(req.content)['results']]
        return [SearchResult(r) for r in json.loads(req.content)['results']]


class SearchResult(object):
    score = 0.0
    resultId = None
    schema = None

    def __init__(self, result_dict):
        self.resultId = result_dict['resultId']
        self.score = result_dict['score']
        schema_list = [x['href'] for x in result_dict['source']['links'] if x['rel'] == 'schema']
        assert(len(schema_list) == 1)
        self.schema = schema_list.pop()
