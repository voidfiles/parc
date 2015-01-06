from collections import defaultdict

import requests
from breadability.readable import Article as ReadableArticle

from .models import Article, Origin
from .url_utils import canonicalize_url


class FailedToCreateArticle(Exception):
    pass


def parse_meta_data(doc):
    if not doc:
        return None

    data = defaultdict(dict)

    for prop in doc.cssselect('meta'):
        key = prop.get('property', prop.get('name'))
        if not key:
            continue

        key = key.split(':')

        value = prop.get('content', prop.get('value'))

        if not value:
            continue

        value = value.strip()

        if value.isdigit():
            value = int(value)

        ref = data[key.pop(0)]

        for idx, part in enumerate(key):
            if not key[idx:-1]:  # no next values
                ref[part] = value
                break
            if not ref.get(part):
                ref[part] = dict()
            else:
                if isinstance(ref.get(part), basestring):
                    ref[part] = {'url': ref[part]}
            ref = ref[part]

    return data


def fetch_url(url):
    try:
        resp = requests.get(url, timeout=15)
    except requests.HTTPError:
        raise FailedToCreateArticle('Something went wrong while trying to fetch the article.')
    except requests.TooManyRedirects:
        raise FailedToCreateArticle('The URL redirected to many times to fetch the article')
    except requests.Timeout:
        raise FailedToCreateArticle('The URL took longer then 15 seconds to fetch.')

    return resp


def set_origin_for_article(article):
    if not article.origin:
        origin, _ = Origin.objects.get_or_create(url=article.domain, defaults={
            'title': article.domain
        })

        article.origin = origin

    return article


def create_article_from_api_obj(article_a):
    url = canonicalize_url(article_a.url)

    try:
        article = Article.objects.get(url=url)
        return article
    except Article.DoesNotExist:
        pass

    resp = fetch_url(url)

    url = canonicalize_url(resp.url)

    try:
        article = Article.objects.get(url=url)
        return article
    except Article.DoesNotExist:
        pass

    document = ReadableArticle(resp.content, url)

    meta_data = parse_meta_data(document.dom)

    title = document.dom.cssselect('title')

    if title:
        title = title[0].text

    if not title:
        title = meta_data.get('og', {}).get('title', None)

    if not title:
        title = meta_data.get('twitter', {}).get('title', None)

    if not title:
        title = None

    article = Article.objects.create(url=url, title=title)

    if 'og' in meta_data:
        article.social_data.og = meta_data['og']

    if 'twitter' in meta_data:
        article.social_data.twitter = meta_data['twitter']

    article.article_info.html = resp.content
    article.article_info.full_text_html = document.readable
    article = set_origin_for_article(article)
    article.processed = True
    article.save()

    if article_a.tags:
        tags = [tag.name for tag in article_a.tags]
        if tags:
            article.tags.add(*tags)

    return article
