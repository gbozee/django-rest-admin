import unittest
from unittest import mock

from mservice_model.api import ServiceApi
from mservice_model.models import ServiceModel, model_factory

from .response import MockRequest, get_all_response, option_response


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.base_url = 'http://localhost:2000/todos/'
        self.service = ServiceApi(self.base_url)
        self.patcher = mock.patch('mservice_model.api.requests')
        self.mock_request = self.patcher.start()
        self.mock_get = self.mock_request.get
        self.mock_post = self.mock_request.post
        self.mock_put = self.mock_request.put
        self.mock_options = self.mock_request.options
        self.mock_delete = self.mock_request.delete
        self.mock_options.return_value = MockRequest(option_response,overwrite=True)

    def tearDown(self):
        self.patcher.stop()
