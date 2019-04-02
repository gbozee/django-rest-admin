import pytest
import unittest
from unittest import mock

from mservice_model.api import ServiceApi
from mservice_model.models import ServiceModel, model_factory

from . import base
from .response import MockRequest, get_all_response, option_response



def test_count_method_in_queryset_returns_correct_value(service, mock_get):
    SampleModel = model_factory(service, name="Sample")
    assert SampleModel.objects.count() == 4


def test_all_methods_returns_all_queryset_result(service, mock_get):
    SampleModel = model_factory(service, name="Sample")
    result = SampleModel.objects.all()
    assert result[0].completed == False
    assert result[0].id == 1
    assert result[0].owner is None


def test_get_method_returns_single_object_based_on_query(
    service, mock_request, base_url
):
    mock_get = mock_request(
        "get", return_value=MockRequest(get_all_response["results"][0], overwrite=True)
    )
    SampleModel = model_factory(service, name="Sample")
    result = SampleModel.objects.get(id=1)
    mock_get.assert_called_once_with("{}{}/".format(base_url, 1))
    assert result.id == 1


def test_create_method_creates_new_instance(service, mock_request):
    mock_post = mock_request(
        "post",
        return_value=MockRequest(
            {"title": "Hello World", "completed": True, "id": 72, "owner": None},
            overwrite=True,
        ),
    )
    SampleModel = model_factory(service, name="Sample")
    result = SampleModel.objects.create(title="Hello world", completed=True)
    assert result.pk == 72
    assert result.owner == None
    assert result.title == "Hello World"
    assert result.completed

