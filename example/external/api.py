import json
from mservice_model.api import Bunch, FetchHelpers, ServiceApi


class FetchAPI(FetchHelpers):

    def get_object_by_id(self, request_id, cls=Bunch):
        data = self._fetch_data('GET', self._path(
            '/requests/{}'.format(request_id)))
        return [self._make_base_request(data, cls)]

    def get_values_list(self, *args, **kwargs):
        field_names = ",".join(args)
        params = {**kwargs, **{'field': field_names}}
        return self._fetch_data('GET', self._path('/requests/values_list'), params=params)


    def get_datetimes(self, field_name, kind, order, filter_query, **kwargs):
        params = dict(field_name=field_name, kind=kind,
                      order=order, filter_query=json.dumps(filter_query))
        return self._fetch_data('GET', self._path('/requests/datetimes'), params=params)

    def get_date_range(self, field_name):
        params = dict(field_name=field_name)
        return self._fetch_data('GET', self._path('/requests/date_range'), params=params)


# instance = FetchAPI("http://192.168.56.101:8000")
instance = ServiceApi("http://192.168.56.101:8000/requests/")
