import unittest
import glob
import pyxus.util as u

class TestJsonld(unittest.TestCase):
    def test_parse(self):
        print 'test_parse'
        for i in glob.glob('./data/*.json'):
            g = u.load_jsonld(i)
            print 'file:' + i
            print u.pretty_jsonld(g)


    # test_json = '''
    # {
    #     "@context": {
    #         "dc": "http://purl.org/dc/terms/",
    #         "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    #         "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
    #     },
    #     "@id": "http://example.org/about",
    #     "dc:title": {
    #         "@language": "en",
    #         "@value": "Someone's Homepage"
    #     }
    # }
    # '''
    # g = Graph().parse(data=test_json, format='json-ld')
    # assert list(g) == [(
    #     URIRef('http://example.org/about'),
    #     URIRef('http://purl.org/dc/terms/title'),
    #     Literal("Someone's Homepage", lang='en'))]




if __name__ == '__main__':
    a = TestJsonld('test_parse')
    a.test_parse()
