import json
from datetime import date, datetime
from decimal import Decimal

import maya
import requests
from django.db.models import fields
from django.db.models.fields import FieldDoesNotExist
from django.utils.functional import cached_property

from mservice_model.fields import AutoField, ListField


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


class FetchHelpers(object):
    """The api class to implement all the api calls responsible
    to get the admin interface to be functional"""

    def __init__(self, url):
        self.base_url = url

    def _make_base_request(self, data, cls):
        """Create an instance of the class passed from the
        response of the dictionary"""
        field_with_types = {
            k: v['type']
            for k, v in self.fields.items()
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

    def _fetch_data(self, method, url, **kwargs):
        method_map = {
            'GET': requests.get,
            'POST': requests.post,
            'PUT': requests.put,
            'DELETE': requests.delete,
            'OPTIONS': requests.options
        }
        request = method_map.get(method)
        response = request(url, **kwargs)
        response.raise_for_status()
        return response.json()

    def _path(self, path=''):
        return self.base_url + path

    def _populate_base_request_fields(self, data):
        result = {}
        options = {
            'decimal': fields.DecimalField,
            'datetime': fields.DateTimeField,
            'integer': fields.IntegerField,
            'string': fields.CharField,
            'email': fields.EmailField,
            'field': fields.CharField,
            'list': ListField,
            'boolean': fields.BooleanField
        }
        for key, value in data.items():
            default_dict = {
                'verbose_name': value['label'],
                'null': value['required'],
            }
            if value['type'] in ["string", "email"]:
                if value.get('max_length'):
                    default_dict.update(max_length=value['max_length'])
            if value['type'] == 'field':
                default_dict.update(max_length=70)
            if key == 'id':
                result[key] = AutoField()
            else:
                result[key] = options[value['type']](**default_dict)

        return result

    @cached_property
    def fields(self):
        return self.get_fields()

    def get_fields(self):
        """Makes an OPTIONS call to the djangorestframework endpoint"""
        fetched_data =  self._fetch_data('OPTIONS', self._path(''))
        return fetched_data['actions']['POST']

    def construct_model_fields(self):
        data = self.fields
        return self._populate_base_request_fields(data)

    def get_datetimes(self, field_name, kind, order, filter_query, **kwargs):
        """API logic to get the list of datetimes"""
        raise NotImplementedError

    def get_date_range(self, field_name):
        """API logic to implent the date ranges for `date_heirachy` in admin"""
        raise NotImplementedError

    def get_values_list(self, *args, **kwargs):
        """API logic to emulate returning queryset as a list of values just like
        django's orm .values_list. takes an optional parameter flat"""
        raise NotImplementedError

    def get_object_by_id(self, request_id, cls=Bunch):
        data = self._fetch_data('GET', self._path(
            '{}/'.format(request_id)))
        return [self._make_base_request(data, cls)]

    def get_all_objects(self, filter_by, order_by, cls):
        params = {**filter_by, **{'field_name': 'modified'}}
        if order_by:
            params.update(ordering=','.join(order_by))
        print(order_by)
        data = self._fetch_data('GET', self._path(''), params=params)
        as_objects = [self._make_base_request(o, cls) for o in data['results']]
        total = data['count']
        date_range = data.get('date_range')
        last_id = data.get('last_id')
        return as_objects, total, date_range, last_id



class ServiceApi(object):

    def __init__(self, api_instance, base_class=FetchHelpers):
        self.instance = FetchHelpers(api_instance)

    def get_data(self, filter_by, order_by, cls=Bunch, **kwargs):
        base_requests = []
        total = 0
        date_range = None
        last_id = None
        new_filter_by = {**filter_by, **kwargs}
        print(new_filter_by)
        if 'pk' in filter_by:
            base_requests = self.instance.get_object_by_id(new_filter_by['pk'],
                                                           cls)
        else:
            base_requests, total, date_range, last_id = self.instance.get_all_objects(new_filter_by,
                                                                                      order_by, cls)
            date_range = self.serialize_date_range(date_range)
        return base_requests, total, date_range, last_id

    def create(self, cls=Bunch, **kwargs):
        as_dict = self.to_serializable_dict(**kwargs)
        return self.instance._make_base_request(as_dict, cls)

    def fetch_date_range(self, field_name):
        return self.instance.get_date_range(field_name)

    def serialize_date_range(self, date_range):
        result = date_range or {}
        if result:
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
        return self.instance.get_datetimes(*args, **kwargs)

    def datetimes(self, *args, **kwargs):
        value = [
            maya.parse(x).datetime("Africa/Lagos")
            for x in self.fetch_datetimes(*args, **kwargs)
        ]
        return value

    def get_values_list(self, *args, **kwargs):
        return self.instance.get_values_list(*args, **kwargs)

    def to_serializable_dict(self, **kwargs):
        """Converts all values of kwargs to a
        serializable value in python"""
        as_string = json.dumps(kwargs, cls=MyEncoder)
        return json.loads(as_string)

    def initialize(self):
        """"""
        return self.instance.construct_model_fields()

