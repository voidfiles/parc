from catalog.schemas import TagSchema

from .base import ParcApiObject


class TagApiObject(ParcApiObject):
    schema = TagSchema

    @classmethod
    def from_model(cls, model, *args, **kwargs):
        data = {
            'id': model.id,
            'name': model.name,
            'slug': model.slug,
            'date_saved': model.created,
            'date_updated': model.updated,
        }

        return cls.get_schema()(data)
