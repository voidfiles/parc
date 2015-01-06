from paucore.utils.python import cast_int
from simpleapi import api_export, SimpleHttpException

from catalog.article import create_article_from_api_obj, FailedToCreateArticle
from catalog.objects import ArticleApiObject
from catalog.models import Article

from .utils import api_object_from_request, api_view, pk_queryset_paginate, paginate_queryset_for_request

article_view = api_view(ArticleApiObject)


@api_export(method='POST', path=r'articles')
@article_view(collection=False)
def create_article(request):
    article_a = api_object_from_request(request, ArticleApiObject)

    try:
        article = create_article_from_api_obj(article_a)
    except FailedToCreateArticle, err:
        raise SimpleHttpException(err.message, 'article-failed-create', code=500)

    return article


@api_export(method='GET', path=r'articles')
@article_view(collection=True)
def get_articles(request):
    articles = Article.objects.all()
    articles = paginate_queryset_for_request(request, articles, pk_queryset_paginate)

    return articles


@api_export(method='GET', path=r'articles/(?P<article_id>[0-9]+)')
@article_view(collection=False)
def get_article(request, article_id):
    article_id = cast_int(article_id, None)
    if article_id is None:
        raise SimpleHttpException('Missing article id.', 'missing-param')

    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        raise SimpleHttpException('Article with ID does not exsits', 'missing', code=404)

    return article
