from catalog.schemas import ArticleSchema, OriginSchema

from .base import ParcApiObject
from .tags import TagApiObject


class OriginApiObject(ParcApiObject):
    schema = OriginSchema

    @classmethod
    def from_model(cls, model, *args, **kwargs):
        data = {
            'title': model.title,
            'url': model.url,
            'date_saved': model.created,
            'date_updated': model.updated
        }

        return cls.get_schema()(data)


class ArticleApiObject(ParcApiObject):
    schema = ArticleSchema

    @classmethod
    def from_request(cls, request, *args, **kwargs):
        data = cls._parse_json_from_request(request, *args, **kwargs)
        obj = cls._deserialize(cls.get_schema(), data)

        return obj

    @classmethod
    def from_model(cls, model, *args, **kwargs):
        data = {
            'id': model.id,
            'title': model.effective_title,
            'url': model.url,
            'date_saved': model.created,
            'date_updated': model.updated,
            'html': model.article_info.full_text_html,
            'deleted': model.deleted,
            'archived': model.archived,
        }

        if model.origin:
            data['origin'] = OriginApiObject.from_model(model.origin)

        data['tags'] = [TagApiObject.from_model(tag) for tag in model.tags.all()]

        return cls.get_schema()(data)
