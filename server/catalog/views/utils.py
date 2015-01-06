from functools import wraps

from paucore.utils.python import cast_int

from schematics.exceptions import ModelValidationError
from simpleapi import SimpleHttpException


def api_object_from_request(request, api_object_cls, **kwargs):
    try:
        api_obj = api_object_cls.from_request(request, **kwargs)
    except ModelValidationError, err:
        raise SimpleHttpException('There was a validation error', error_slug='validation',
                                  code=400, info=err.messages)

    return api_obj


def api_view(api_obj):

    def _api_view(collection):

        def wrapper(f):
            @wraps(f)
            def inner(request, *args, **kwargs):
                objs = f(request, *args, **kwargs)
                if collection:
                    return [api_obj.from_model(obj).to_primitive() for obj in objs]
                else:
                    return api_obj.from_model(objs).to_primitive()

            return inner

        return wrapper

    return _api_view


def pk_queryset_paginate(params, queryset):
    before_id = cast_int(params.get('before_id'), default=None)
    since_id = cast_int(params.get('since_id'), default=None)
    count = cast_int(params.get('count'), default=20, bounds=(1, 200))

    queryset = queryset.order_by('-pk')

    filter_kwarg = {}
    if before_id is not None:
        filter_kwarg['pk__lt'] = before_id

    if since_id is not None:
        filter_kwarg['pk__gt'] = since_id

    queryset = queryset.filter(**filter_kwarg)

    queryset = queryset[0:count + 1]

    num_objects = queryset.count()
    has_more = False
    if num_objects > count:
        has_more = True

    objs = list(queryset[0:count])
    meta_data = {
        'has_more': has_more
    }

    if objs:
        meta_data['max_id'] = objs[0].pk
        meta_data['min_id'] = objs[-1].pk

    return objs, meta_data


def paginate_queryset_for_request(request, queryset, paginator):
    queryset, metadata = paginator(request.GET, queryset)
    request.META['_simple_api_meta'].update(metadata)

    return queryset
