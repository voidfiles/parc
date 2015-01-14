from urlparse import urlparse

from django.db import models
from taggit.managers import TaggableManager
from taggit.models import ItemBase, TagBase

from paucore.data.fields import (CreateDateTimeField, LastModifiedDateTimeField,
                                 DictField, Choices)
from paucore.data.pack2 import (Pack2, SinglePack2Container, PackField)

from .url_utils import canonicalize_url


class Tag(TagBase):
    extra = DictField(default=dict)
    created = CreateDateTimeField()
    updated = LastModifiedDateTimeField()

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


class TaggedArticle(ItemBase):
    tag = models.ForeignKey(Tag, related_name="%(app_label)s_%(class)s_items")
    content_object = models.ForeignKey('Article')
    extra = DictField(default=dict)
    created = CreateDateTimeField()
    updated = LastModifiedDateTimeField()

    @classmethod
    def tags_for(cls, model, instance=None):
        if instance is not None:
            return cls.tag_model().objects.filter(**{
                '%s__content_object' % cls.tag_relname(): instance
            })
        return cls.tag_model().objects.filter(**{
            '%s__content_object__isnull' % cls.tag_relname(): False
        }).distinct()


class Origin(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True, unique=True)
    created = CreateDateTimeField()
    updated = LastModifiedDateTimeField()
    extra = DictField(default=dict)


def normalise(output):
    if not output:
        return ''

    return output


class SocialDatum(dict):

    def __repr__(self):
        return normalise(self.get('og', self.get('twitter', '')))

    def __unicode__(self):
        return normalise(self.get('og', self.get('twitter', '')))

    @property
    def twitter(self):
        return normalise(self.get('twitter', ''))

    @property
    def open_graph(self):
        return normalise(self.get('og', ''))


class SocialData(Pack2):
    open_graph = PackField(key='o', docstring='Open Graph Meta Data', null_ok=True, default=lambda x: dict())
    twitter = PackField(key='t', docstring='Twitter Metadata', null_ok=True, default=lambda x: dict())

    def get_social_value(self, key):
        if self.open_graph and self.open_graph.get(key):
            return self.open_graph[key]

        if self.twitter and self.twitter.get(key):
            return self.twitter[key]

        return None

    @property
    def description(self):
        return self.get_social_value('description')

    @property
    def title(self):
        return self.get_social_value('title')


class ArticleInfo(Pack2):
    author = PackField(key='a', docstring='author info', null_ok=True)
    full_html = PackField(key='h', docstring='Full html of article', null_ok=True)
    full_text_html = PackField(key='t', docstring='Full html of main text in article', null_ok=True)


ARTICLE_STATUS = Choices(
    (1, 'UNREAD', 'Unread'),
    (2, 'ARCHIVED', 'Archived'),
    (10, 'DELETED', 'Deleted'),
)


class ArticleManger(models.Manager):
    def for_url(self, url):
        url = canonicalize_url(url)

        try:
            article = self.get(url=url)
        except self.model.DoesNotExist:
            return None, url

        return article, url


class Article(models.Model):
    title = models.TextField(max_length=1000, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True, unique=True)
    processed = models.BooleanField(default=False)
    created = CreateDateTimeField()
    updated = LastModifiedDateTimeField()
    origin = models.ForeignKey(Origin, blank=True, null=True)
    extra = DictField(default=dict)
    status = models.IntegerField(choices=ARTICLE_STATUS, default=ARTICLE_STATUS.UNREAD)

    social_data = SinglePack2Container(pack_class=SocialData, field_name='extra', pack_key='s')
    article_info = SinglePack2Container(pack_class=ArticleInfo, field_name='extra', pack_key='a')

    tags = TaggableManager(through=TaggedArticle)
    objects = ArticleManger()

    def __repr__(self):
        return '<SiteArticle %r>' % (self.title,)

    @property
    def domain(self):
        parts = urlparse(self.url)
        netloc = parts.netloc
        return netloc.replace('www.', '')

    @property
    def effective_title(self):
        social_title = self.social_data.title
        if social_title:
            return social_title

        return self.title
