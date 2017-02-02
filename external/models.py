from mservice_model.models import ServiceModel
from mservice_model.manager import ServiceManager
from mservice_model.queryset import ServiceQuerySet
from mservice_model.options import ServiceOptions
from django.db.models import fields
# Create your models here.
from external import api as request_api


class BaseRequestTutorQuerySet(ServiceQuerySet):
    pass


class BaseRequestTutorManager(ServiceManager):
    queryset = BaseRequestTutorQuerySet


class BaseRequestTutor(ServiceModel):
    _default_manager = BaseRequestTutorManager
    _service_api = request_api.RequestAPI()

    class Meta(ServiceOptions):
        _service_fields = request_api.get_request_fields()
        ordering = ('id',)
        verbose_name = "Client Request Detail"

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "<BaseRequestTutor {}>".format(self.email)

BaseRequestTutor._meta._bind()