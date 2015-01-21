from schematics.types import BaseType, StringType, URLType, DateTimeType, BooleanType
from schematics.types.compound import ModelType, ListType
from schematics.exceptions import ValidationError

from .base import ParcSchema
from .tags import TagSchema

PARC_ISO_STRF_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class StringIntType(BaseType):
    def to_native(self, value):
        try:
            value = int(value)
            return value
        except:
            return

    def validate_stringint(self, value):
        try:
            value = int(value)
        except:
            ValidationError('"%s" is not a valid id' % value)

    def to_primitive(self, value, context=None):
        return unicode(value)


class OriginSchema(ParcSchema):
    title = StringType()
    url = URLType()
    date_saved = DateTimeType(serialized_format=PARC_ISO_STRF_FORMAT)
    date_updated = DateTimeType(serialized_format=PARC_ISO_STRF_FORMAT)


class ArticleSchema(ParcSchema):
    id = StringIntType()
    url = URLType(required=True)
    title = StringType()
    html = StringType()
    date_saved = DateTimeType(serialized_format=PARC_ISO_STRF_FORMAT)
    date_updated = DateTimeType(serialized_format=PARC_ISO_STRF_FORMAT)
    origin = ModelType(OriginSchema)
    tags = ListType(ModelType(TagSchema))
    archived = BooleanType()
    deleted = BooleanType()
