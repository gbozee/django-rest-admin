from django.test import TestCase
from mservice_model.api import ServiceApi,Bunch
from unittest import mock
from .response import MockRequest, option_response, get_all_response
from .test_models import BaseTestCase


class ServiceApiTestCase(BaseTestCase):
    def setUp(self):
        
        super().setUp()
        self.mock_options.return_value = MockRequest(option_response,overwrite=True)
        
    def test_correct_fields_are_returned(self):
        instance = ServiceApi(self.base_url)      
        self.assertEqual(instance.instance.fields, option_response['actions']['POST'])
        
    def test_get_all_objects(self):
        self.mock_get.return_value = MockRequest(get_all_response, overwrite=True)
        instance = ServiceApi(self.base_url)
        response = instance.instance.get_all_objects({},None,Bunch)
        self.assertEqual(response[1], 4)
        self.assertEqual(response[3], 4)