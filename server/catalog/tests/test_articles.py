from django.test import TestCase
import json
import os
import responses

DEFAULT_ARTICLE_URL = 'http://recode.net/2014/12/04/amazon-unveils-its-own-line-of-diapers-confirming-partners-biggest-fears/'

BASE_DIR = os.path.dirname(__file__) + '/data/'

DEFAULT_ARTICLE_CONTENT = ''
with open(BASE_DIR + 'article.html') as fd:
    DEFAULT_ARTICLE_CONTENT = fd.read()

BASE_DIR = os.path.dirname(__file__) + '/data/'
CASSETTE_DIR = BASE_DIR + '/cassettes/'


class MockModel(object):
    DEFAULT_ARTICLE_CONTENT = DEFAULT_ARTICLE_CONTENT
    CASSETTE_DIR = CASSETTE_DIR
    DEFAULT_ARTICLE_URL = DEFAULT_ARTICLE_URL

    def add_article_content_to_responses(self, url=DEFAULT_ARTICLE_URL, body=DEFAULT_ARTICLE_CONTENT):
        responses.add(responses.GET, url,
                      body=body, status=200,
                      content_type='text/html')


class TestArticles(MockModel, TestCase):
    def test_add_article(self):
        self.add_article_content_to_responses()

        response = self.client.post('/api/v1/articles', json.dumps({
            'url': self.DEFAULT_ARTICLE_URL,
            'tags': [{'name': 'diaper'}, {'name': 'DIAPER'}]
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)

        self.assertEquals(resp['data']['title'], "Amazon Unveils Its Own Diapers and Baby Wipes Called Amazon Elements | Re/code")

    def test_add_article_failure(self):

        response = self.client.post('/api/v1/articles', json.dumps({
            'url': 'awesome'
        }), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)

        self.assertEquals(resp['meta']['error_info']['url'][0], "Not a well formed URL.")

    def test_article_pagination(self):
        base_url = 'http://example.com/article/%s'
        for i in range(0, 20):
            url = base_url % i
            self.add_article_content_to_responses(url=url)

            response = self.client.post('/api/v1/articles', json.dumps({
                'url': url,
            }), content_type='application/json')

        response = self.client.get('/api/v1/articles?count=10')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        assert len(resp['data']) == 10
        assert resp['meta']['min_id'] > 1
