from django.db.models import fields
from django.db.models import ForeignKey
from django.apps import apps

from .utils import CachedPropertiesMixin

class ServiceAutoField(fields.AutoField):
    def to_python(self, value):
        return value

DEFAULT_NAMES = (
    'verbose_name', 'verbose_name_plural', 
    'app_label', 'auto_created', 'apps', 'default_related_name', 
    'object_name', 'verbose_name_raw','model_name'
)

class ServiceOptions(CachedPropertiesMixin):
    has_auto_field = True
    auto_created = False 
    abstract = False
    swapped = False
    virtual_fields = []
    _other_fields = {}
    _service_fields = {}
    apps = apps

    def add_field(self, *args, **kwargs):
        pass

    def __init__(self, **kwargs):
        """overide parent fields"""
        if 'path' in kwargs:
            value = kwargs['path']
            s = value.split('.')
            self.app_label = s[0]
            self.model_name = s[-1]
            self.verbose_name = s[-1]
            self.verbose_name_raw = s[-1]
            self.verbose_name_plural = "{}s".format(s[-1])
            self.object_name = s[-1]
            
    
    def _bind(self):
        for field_name, field in self._other_fields.items():
            setattr(self, field_name, field)
            field.set_attributes_from_name(field_name)
        self.pk = self._service_fields[self._service_pk_field]

    def get_fields(self, **kwargs):
        return self._get_fields()

    def get_field(self, field_name):
        try:
            all_fields = {**self._service_fields, **self._other_fields}
            return all_fields[field_name]
        except KeyError:
            raise fields.FieldDoesNotExist()
    
    def _get_fields(self, reverse=True, forward=True):
        all_fields = {**self._service_fields, **self._other_fields}            
        return tuple([field for field_name, field in all_fields.items()])