from django.test import TestCase
import json
import os
import responses

from catalog.models import Article, ARTICLE_STATUS


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
    def create_article(self):
        with responses.mock:
            self.add_article_content_to_responses()

            response = self.client.post('/api/v1/articles', json.dumps({
                'url': self.DEFAULT_ARTICLE_URL,
                'tags': [{'name': 'diaper'}, {'name': 'DIAPER'}]
            }), content_type='application/json')

        return response

    def test_add_article(self):
        response = self.create_article()

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
        with responses.mock:
            for i in range(0, 20):
                url = base_url % i
                self.add_article_content_to_responses(url=url)

                response = self.client.post('/api/v1/articles', json.dumps({
                    'url': url,
                }), content_type='application/json')
                resp = json.loads(response.content)
                self.assertEqual(response.status_code, 200)

            response = self.client.get('/api/v1/articles?count=10')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        assert len(resp['data']) == 10
        assert resp['meta']['min_id'] > 1

    def test_article_delete(self):
        response = self.create_article()
        resp = json.loads(response.content)
        response = self.client.delete('/api/v1/articles/%s' % (resp['data']['id']))
        self.assertEqual(response.status_code, 200)

        article = Article.objects.get(id=resp['data']['id'])
        self.assertEqual(article.status, ARTICLE_STATUS.DELETED)

    def test_article_archive(self):
        response = self.create_article()
        resp = json.loads(response.content)
        response = self.client.post('/api/v1/articles/%s/archive' % (resp['data']['id']))
        self.assertEqual(response.status_code, 200)

        article = Article.objects.get(id=resp['data']['id'])
        self.assertEqual(article.status, ARTICLE_STATUS.ARCHIVED)

    def test_article_unarchive(self):
        response = self.create_article()
        resp = json.loads(response.content)
        response = self.client.delete('/api/v1/articles/%s/archive' % (resp['data']['id']))
        self.assertEqual(response.status_code, 200)

        article = Article.objects.get(id=resp['data']['id'])
        self.assertEqual(article.status, ARTICLE_STATUS.UNREAD)
