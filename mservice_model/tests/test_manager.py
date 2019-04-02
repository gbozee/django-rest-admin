import pytest
from mservice_model.models import ServiceModel, model_factory
from django.db import models
from mservice_model.exceptions import ServiceException

def test_create_fields_like_django_models(service, mock_get):
    with pytest.raises(ServiceException) as e:
        class Sample(ServiceModel):
            title = models.CharField()
            completed = models.BooleanField()
            owner = models.CharField()

            class Meta:
                app_label = "sample"
    assert e._excinfo[1].message == 'Did you forget to add an `id` model field?'
