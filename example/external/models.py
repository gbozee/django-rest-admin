from mservice_model.models import ServiceModel
from mservice_model.options import ServiceOptions
from django.db.models import fields
# Create your models here.
from external.api import instance as request_api

class BaseRequestTutor(ServiceModel):
    _service_api = request_api

    class Meta:
        ordering = ('id',)
        verbose_name = "Client Request Detail"



    def __repr__(self):
        return "<BaseRequestTutor {}>".format(self.email)
