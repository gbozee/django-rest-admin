from unittest import mock
import pytest
from mservice_model.api import Bunch, ServiceApi
from django.db import models
from . import base
from .response import MockRequest, get_all_response, option_response


def test_get_fields(service,mock_request):
    fields = service.initialize()
    assert isinstance(fields['title'],models.CharField)

class ServiceApiTestCase(base.BaseTestCase):
    def setUp(self):
        
        super().setUp()
        self.mock_options.return_value = MockRequest(option_response,overwrite=True)
        self.service = ServiceApi(self.base_url)      

    def test_correct_fields_are_returned(self):
        self.assertEqual(self.service.instance.fields, option_response['actions']['POST'])
        
    def test_get_all_objects(self):
        self.mock_get.return_value = MockRequest(get_all_response, overwrite=True)
        response = self.service.instance.get_all_objects({},None,Bunch)
        self.assertEqual(response[1], 4)
        self.assertEqual(response[3], 4)



