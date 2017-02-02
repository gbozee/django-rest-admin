import json
from datetime import date, datetime
from decimal import Decimal

import maya
from django.db.models.fields import FieldDoesNotExist


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)

        return json.JSONEncoder.default(self, obj)


class Bunch(object):
    def __init__(self, *args, **kwargs):
        self.__dict__ = kwargs
        self.pk = self.id

    def __unicode__(self):
        return self.id

    def serializable_value(self, field_name):
        try:
            field = self._meta.get_field(field_name)
        except FieldDoesNotExist:
            return getattr(self, field_name)
        return getattr(self, field.attname)


class ServiceApi(object):
    def get_data(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, cls=Bunch, **kwargs):
        raise NotImplementedError

    def fetch_date_range(self, field_name):
        raise NotImplementedError

    def serialize_date_range(self, date_range):
        result = date_range
        result.update(first=maya.when(result['first']).datetime())
        result.update(last=maya.when(result['last']).datetime())
        return result

    def aggregate(self, **kwargs):
        aliases = [x.default_alias for key, x in kwargs.items()]
        field_name = aliases[0].split('__')[0]
        result = self.fetch_date_range(field_name)
        if 'first' in kwargs.keys():
            result.update(first=maya.when(result['first']).datetime())
        if 'last' in kwargs.keys():
            result.update(last=maya.when(result['last']).datetime())
        return result

    def fetch_datetimes(self, *args, **kwargs):
        raise NotImplementedError

    def datetimes(self, *args, **kwargs):
        value =  [
            maya.parse(x).datetime("Africa/Lagos")
            for x in self.fetch_datetimes(*args, **kwargs)
        ]
        return value

    def to_serializable_dict(self, **kwargs):
        """Converts all values of kwargs to a
        serializable value in python"""
        as_string = json.dumps(kwargs, cls=MyEncoder)
        return json.loads(as_string)


class FetchHelpers(object):
    def _make_base_request(self, data, cls):
        """Create an instance of the class passed from the
        response of the dictionary"""
        field_with_types = {
            k: v['type']
            for k, v in self.get_request_fields.items()
        }
        options = {
            'decimal': lambda x: Decimal(x) if x else None,
            'datetime': lambda x: maya.parse(x).datetime() if x else None,
        }
        new_data = {}
        for key, value in data.items():
            inst = field_with_types[key]
            try:
                result = options[inst](value)
            except KeyError:
                result = value
            new_data.update({key: result})
        return cls(**new_data)
