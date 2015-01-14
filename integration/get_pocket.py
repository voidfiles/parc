import logging
from datetime import datetime
import lxml.html
from schematics.exceptions import ModelValidationError

from catalog.article import create_article_from_api_obj, FailedToCreateArticle
from catalog.objects import ArticleApiObject
from catalog.models import ARTICLE_STATUS

logger = logging.getLogger(__name__)


def el_to_article_a(link):
    article_info = {}
    article_info['title'] = link.text
    article_info['url'] = link.attrib['href']
    article_info['date_saved'] = article_info['date_updated'] = datetime.fromtimestamp(int(link.attrib['time_added']))
    if link.attrib['tags']:
        article_info['tags'] = [{'name': tag.lower()} for tag in link.attrib['tags'].split(',')]

    try:
        article_a = ArticleApiObject.from_data(article_info)
    except ModelValidationError:
        return None

    return article_a


def parse_pocket_export(html):
    document = lxml.html.fromstring(html)

    prospective_articles = {}

    body = document.find('body')
    section = None
    for child in body:
        if child.tag.lower() == 'h1':
            section = child.text.lower()
            prospective_articles[section] = []

            continue

        if child.tag.lower() == 'ul' and section:
            for li in child:
                article_a = el_to_article_a(li.find('a'))
                if article_a:
                    prospective_articles[section].append(article_a)

    return prospective_articles


def process_articles(html):
    prospective_articles = parse_pocket_export(html)
    if 'unread' in prospective_articles:
        for article_a in prospective_articles['unread']:
            try:
                logger.info("Adding %s to unread", article_a.url)
                create_article_from_api_obj(article_a, use_time_info=True)
            except FailedToCreateArticle:
                continue

    if 'read archive' in prospective_articles:
        for article_a in prospective_articles['read archive']:
            try:
                logger.info("Adding %s to archive", article_a.url)
                create_article_from_api_obj(article_a, use_time_info=True, status=ARTICLE_STATUS.ARCHIVED)
            except FailedToCreateArticle:
                continue
