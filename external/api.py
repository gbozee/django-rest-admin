from mservice_model.api import ServiceApi, Bunch, FetchHelpers
import requests
from mservice_model.fields import ListField, AutoField
from django.db.models import fields
from django.utils.functional import cached_property
import json
import datetime

# from django.contrib.postgres.fi import fields as postgres_fields


class FetchAPI(FetchHelpers):
    def __init__(self, url):
        self.base_url = url

    def get_request_by_id(self, request_id, cls=Bunch):
        response = requests.get("{}/requests/{}/".format(self.base_url,
                                                         request_id))
        response.raise_for_status()
        data = response.json()
        return [self._make_base_request(data, cls)]

    def construct_model_fields(self):
        data = self.get_request_fields
        return self._populate_base_request_fields(data)

    @cached_property
    def get_request_fields(self):
        response = requests.options("{}/requests/".format(self.base_url))
        response.raise_for_status()
        return response.json()['actions']['POST']

    def get_all_requests(self, filter_by, cls):
        params = {'field_name': 'modified'}
        params = {**filter_by, **params}
        # import ipdb; ipdb.set_trace()
        response = requests.get("{}/requests/".format(self.base_url),
                                params=params)
        response.raise_for_status()
        data = response.json()
        as_objects = [self._make_base_request(o, cls) for o in data['results']]
        total = data['count']
        date_range = data.get('date_range')
        last_id = data.get('last_id')
        return as_objects, total, date_range, last_id

    def get_datetimes(self, field_name, kind, order="ASC", filter_query={}, **kwargs):
        params = dict( field_name=field_name, kind=kind, order=order, filter_query=json.dumps(filter_query))
        response = requests.get("{}/requests/datetimes".format(self.base_url),
                                params=params)
        response.raise_for_status()
        return response.json()

    def get_date_range(self, field_name):
        params = dict(field_name=field_name)
        response = requests.get("{}/requests/date_range".format(self.base_url),
                                params=params)
        response.raise_for_status()
        return response.json()

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
                default_dict.update(max_length=value['max_length'])
            if value['type'] == 'field':
                default_dict.update(max_length=70)
            if key == 'id':
                result[key] = AutoField()
            else:
                result[key] = options[value['type']](**default_dict)

        return result


class RequestAPI(ServiceApi):
    def get_data(self, filter_by, cls=Bunch, **kwargs):
        base_requests = []
        total = 0
        date_range = None
        last_id = None
        print(filter_by)
        if cls.__name__ == 'BaseRequestTutor':
            if 'pk' in filter_by:
                base_requests = instance.get_request_by_id(filter_by['pk'],
                                                           cls)
            else:
                base_requests, total, date_range, last_id = instance.get_all_requests(filter_by,
                    cls)
                date_range = self.serialize_date_range(date_range)
        return base_requests, total, date_range, last_id

    def create(self, cls=Bunch, **kwargs):
        as_dict = self.to_serializable_dict(**kwargs)
        return instance._make_base_request(as_dict, cls)

    def fetch_date_range(self, field_name):
        return instance.get_date_range(field_name)

    def fetch_datetimes(self, *args, **kwargs):
        return instance.get_datetimes(*args, **kwargs)


instance = FetchAPI("http://192.168.56.101:8000")
get_request_fields = instance.construct_model_fields