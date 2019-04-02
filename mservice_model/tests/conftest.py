import pytest
from mservice_model.api import ServiceApi
from mservice_model.models import ServiceModel, model_factory

from .response import MockRequest, get_all_response, option_response


@pytest.fixture
def base_url():
    return "http://localhost:2000/todos/"


@pytest.fixture
def service(base_url):
    return ServiceApi(base_url)


@pytest.fixture
def mock_request(mocker):
    patcher = mocker.patch("mservice_model.api.requests")
    mock_options = patcher.options
    mock_options.return_value = MockRequest(option_response, overwrite=True)

    def _method(method, return_value=None):
        options = {
            "get": patcher.get,
            "post": patcher.post,
            "put": patcher.put,
            "options": patcher.options,
            "delete": patcher.delete,
        }
        value = options[method]
        value.return_value = return_value
        return value

    return _method


@pytest.fixture
def mock_get(mock_request):
    return mock_request(
        "get", return_value=MockRequest(get_all_response, overwrite=True)
    )

