import re


class SearchResult(object):
    score = 0.0
    result_id = None
    schema = None
    self_link = None

    def __init__(self, result_dict):
        self.result_id = result_dict['resultId']
        self.score = result_dict['score']

        links = result_dict['source']['links']
        schema_list = [x['href'] for x in links if x['rel'] == 'schema']
        self.self_link = str([x['href'] for x in links if x['rel'] == 'self'][0])
        assert(len(schema_list) == 1)
        self.schema = schema_list.pop()

    def __unicode__(self):
        '(result_id:{},schema:{}'.format(self.result_id, self.schema)


class SearchResultInstance(object):
    raw_result = None
    instance = None

    def __init__(self, raw_result):
        self.raw_result = raw_result
        self.instance = self._simplify_result(raw_result)

    def _simplify_result(self, json):
        simple = {}
        for key in json:
            if not key.startswith("@"):
                new_key = re.sub(".*?:", "", key)
                if type(json[key]) is dict:
                    simple[new_key] = self._simplify_result(json[key])
                else:
                    simple[new_key] = json[key]
        return simple
