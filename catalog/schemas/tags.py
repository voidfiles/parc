from schematics.types import StringType, IntType, DateTimeType

from .base import ParcSchema


def lower(value):
    if not value:
        return value

    return value.lower()


class TagSchema(ParcSchema):
    id = IntType()
    name = StringType(validators=[lower])
    slug = StringType()
    date_saved = DateTimeType()
    date_updated = DateTimeType()
