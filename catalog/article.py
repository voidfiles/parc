from collections import defaultdict

import requests
from lxml.etree import tounicode
from breadability.readable import Article as ReadableArticle

from .models import Article, Origin, ARTICLE_STATUS


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
    except requests.ConnectionError:
        raise FailedToCreateArticle('The URL could not be found')

    return resp


def set_origin_for_article(article):
    if not article.origin:
        origin, _ = Origin.objects.get_or_create(url=article.domain, defaults={
            'title': article.domain
        })

        article.origin = origin

    return article


def additional_cleaning(dom):
    for empty in dom.xpath('//*[not(node())]'):
        empty.getparent().remove(empty)

    for tag in dom.xpath('//*[@class]'):
        # For each element with a class attribute, remove that class attribute
        tag.attrib.pop('class')

    translations = [('h5', 'h6'), ('h4', 'h5'), ('h3', 'h4'), ('h2', 'h3'), ('h1', 'h2')]
    for _from, to in translations:
        for el in dom.xpath('//%s' % _from):
            el.tag = to

    return dom


def valid_content_type(content_type):
    if not content_type:
        return True

    content_type = [x.strip() for x in content_type.split(';')][0]

    if content_type not in ['text/html', 'application/xhtml+xml']:
        return False

    return True


def create_article_from_api_obj(article_a, use_time_info=False, status=ARTICLE_STATUS.UNREAD):
    article, url = Article.objects.for_url(article_a.url)
    if article:
        return article

    resp = fetch_url(url)

    if resp.status_code != 200:
        raise FailedToCreateArticle('The URL for that article could not be fetched')

    if not valid_content_type(resp.headers.get('content-type')):
        raise FailedToCreateArticle('Parc could not determin the content-type of url')

    article, url = Article.objects.for_url(article_a.url)
    if article:
        return article

    document = ReadableArticle(resp.content, url)
    if not document.dom:
        raise FailedToCreateArticle('Document not HTML')

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

    kwargs = {
        "url": url,
        "title": title,
        "status": status,
    }

    if use_time_info:
        if article_a.date_saved:
            kwargs['created'] = article_a.date_saved

        if article_a.date_updated:
            kwargs['updated'] = article_a.date_updated

    article = Article.objects.create(**kwargs)

    if 'og' in meta_data:
        article.social_data.og = meta_data['og']

    if 'twitter' in meta_data:
        article.social_data.twitter = meta_data['twitter']

    article.article_info.html = resp.content
    readable_dom = additional_cleaning(document.readable_dom)
    article.article_info.full_text_html = tounicode(readable_dom)

    article = set_origin_for_article(article)
    article.processed = True
    article.save()

    if article_a.tags:
        tags = [tag.name for tag in article_a.tags]
        if tags:
            article.tags.add(*tags)

    return article
