from django.test import TestCase
import os
import responses

BASE_DIR = os.path.dirname(__file__) + '/data/'

RIL_EXPORT = ''
with open(BASE_DIR + 'ril_export.html') as fd:
    RIL_EXPORT = fd.read()

BASIC_HTML = """
    <html>
        <head><title>awesome sauce</title></head>
        <body>
            <p>Hello</p>
            <p>Thundercats bitters Neutra ullamco, <a href='http://example.com'>mixtape</a> artisan synth health goth. Mumblecore reprehenderit quinoa sint, trust fund dreamcatcher American Apparel Helvetica deep v pariatur sartorial put a bird on it. Ullamco eiusmod odio Intelligentsia letterpress. Eiusmod duis health goth, try-hard velit do Tumblr fashion axe tote bag flexitarian. Helvetica farm-to-table leggings, post-ironic master cleanse irony nulla whatever occupy. Paleo cornhole lo-fi Williamsburg. Ex 8-bit four dollar toast master cleanse ennui twee lumbersexual, laborum whatever accusamus Helvetica vegan enim.</p>
            <p><span><a href='mailto:aweseom'></a></span></p>
        </body>
    </html>"""

IMPORT_URLS = [
    "http://www.niemanlab.org/2012/10/clay-christensen-on-the-news-industry-we-didnt-quite-understand-how-quickly-things-fall-off-the-cliff/",
    "http://thoughtcatalog.com/brandon-gorrell/2013/10/10-young-people-on-how-they-landed-their-awesome-jobs/",
    "http://www.theverge.com/2014/1/13/5303932/the-fabulous-lives-of-venture-capital-kingmakers-ken-ben-lerer-profile",
]


class TestPocket(TestCase):
    def test_parse_pocket_export(self):
        from integration.get_pocket import parse_pocket_export

        pocket_articles = parse_pocket_export(RIL_EXPORT)

        assert 'unread' in pocket_articles
        assert 'read archive' in pocket_articles

        assert len(pocket_articles['read archive']) == 1

    def test_process_articles(self):
        from integration.get_pocket import process_articles
        from catalog.models import Article, ARTICLE_STATUS, TaggedArticle, Tag

        with responses.mock:
            for url in IMPORT_URLS:
                responses.add(responses.GET, url,
                              body=BASIC_HTML, status=200,
                              content_type='text/html')

            process_articles(RIL_EXPORT)

        articles = Article.objects.filter(url=IMPORT_URLS[0])
        assert articles.count() == 1

        articles = Article.objects.filter(url=IMPORT_URLS[2])
        assert articles.count() == 1
        assert articles[0].status == ARTICLE_STATUS.ARCHIVED

        assert TaggedArticle.objects.all().count() == 2
        assert Tag.objects.all().count() == 2

