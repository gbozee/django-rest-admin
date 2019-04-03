import pytest
from mservice_model.fields import ForeignKey
from mservice_model.models import ServiceModel, model_factory
from django.db import models
from mservice_model.exceptions import ServiceException
from .response import MockRequest, get_all_response


def test_create_fields_like_django_models(service, mock_get):
    with pytest.raises(ServiceException) as e:

        class Sample(ServiceModel):
            title = models.CharField()
            completed = models.BooleanField()
            owner = models.CharField()

            class Meta:
                app_label = "sample"

    assert e._excinfo[1].message == "Did you forget to add an `id` model field?"


def test_foreign_key_relationship(mock_request, service):
    mock_post = mock_request(
        "post",
        side_effect=[
            MockRequest(
                {"title": "Aloiba", "completed": False, "id": 72, "owner": None},
                overwrite=True,
            ),
            MockRequest({"id": 1, "sample_id": 72}, overwrite=True),
        ],
    )
    mock_get = mock_request(
        "get",
        return_value=MockRequest(
            {"title": "Aloiba", "completed": False, "id": 72, "owner": None},
            overwrite=True,
        ),
    )

    class Sample(ServiceModel):
        id = models.AutoField()
        title = models.CharField()
        completed = models.BooleanField()
        owner = models.CharField()
        _service_api = service

        class Meta:
            app_label = "sample"

    class Sample2(ServiceModel):
        id = models.AutoField()
        sample = ForeignKey(Sample, related_name="samples", on_delete=models.SET_NULL)
        _service_api = service

        class Meta:
            app_label = "sample2"

    first_sample = Sample.objects.create(title="Aloiba", completed=True)
    assert first_sample.id == 72
    second_sample = Sample2.objects.create(sample=first_sample)
    assert second_sample.id == 1
    assert second_sample.sample == first_sample

