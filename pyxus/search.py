
import json
import requests

import pyxus.util as util

test_result = '''{u'resultId': u'https://nexus.humanbrainproject.eu/v0/data/hbp/experiment/subject/v0.0.5/44adb543-e430-4600-b852-8a8e3b075679',
   u'score': 0.625,
   u'source': {u'@id': u'https://nexus.humanbrainproject.eu/v0/data/hbp/experiment/subject/v0.0.5/44adb543-e430-4600-b852-8a8e3b075679',
    u'links': [{u'href': u'https://nexus.humanbrainproject.eu/v0/data/hbp/experiment/subject/v0.0.5/44adb543-e430-4600-b852-8a8e3b075679',
      u'rel': u'self'},
     {u'href': u'https://nexus.humanbrainproject.eu/v0/schemas/hbp/experiment/subject/v0.0.5',
      u'rel': u'schema'}]}}'''
