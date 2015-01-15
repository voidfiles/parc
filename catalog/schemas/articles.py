from schematics.types import StringType, IntType, URLType, DateTimeType, BooleanType
from schematics.types.compound import ModelType, ListType

from .base import ParcSchema
from .tags import TagSchema


class OriginSchema(ParcSchema):
    title = StringType()
    url = URLType()
    date_saved = DateTimeType()
    date_updated = DateTimeType()


class ArticleSchema(ParcSchema):
    id = IntType()
    url = URLType(required=True)
    title = StringType()
    html = StringType()
    date_saved = DateTimeType()
    date_updated = DateTimeType()
    origin = ModelType(OriginSchema)
    tags = ListType(ModelType(TagSchema))
    archived = BooleanType()
    deleted = BooleanType()
