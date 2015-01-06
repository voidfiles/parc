import json

from schematics.models import Model
from simpleapi import SimpleHttpException


class ParcApiObject(Model):
    @classmethod
    def _parse_json_from_request(cls, request, *args, **kwargs):
        mimetype = request.META.get('CONTENT_TYPE')
        if not mimetype.startswith('application/json'):
            raise SimpleHttpException('API only supports content type of application/json', 'content-type')

        try:
            data = json.loads(request.body)
        except:
            raise SimpleHttpException('Could not parse json in request body', 'bad-json')

        return data

    @classmethod
    def from_data(cls, data, *args, **kwargs):
        obj = cls._deserialize(cls.get_schema(), data)

        return obj

    @classmethod
    def from_request(cls, request, **kwargs):
        pass

    @staticmethod
    def _deserialize(schema, serialized_data):
        obj = schema(serialized_data)
        obj.validate()
        return obj

    @classmethod
    def get_schema(cls):
        return cls.schema
