from six import with_metaclass

from django.db.models.base import ModelState
from django.db.models.fields import FieldDoesNotExist
# Create your models here.
from .options import ServiceOptions


class ClassProperty(property):
    """converts a class method to a class property. This is
    a convineince for django's objects property"""

    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class ServiceBaseModel(object):
    _deferred = False
    _state = ModelState()
    # _default_manager = ServiceManager
    # _meta = ServiceModel(path="mservice_model.s_model")
    # objects = ClassProperty(classmethod(lambda cls: cls._default_manager(cls)))
    pk = property(lambda self: self.id)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __unicode__(self):
        """expects the model to have an id field"""
        return self.id

    def __eq__(self, other):
        if isinstance(other, ServiceModel):
            return self.pk == other.pk
        return False

    def serializable_value(self, field_name):
        """Returns the serializable value of a field in the model"""
        try:
            field = self._meta.get_field(field_name)
        except FieldDoesNotExist as e:
            return getattr(self, field_name)
        return getattr(self, field.attname)

    def full_clean(self, *args, **kwargs):
        pass

    def validate_unique(self, *args, **kwargs):
        pass

    def _get_pk_val(self):
        pass

class constructor(type):
    def __new__(cls, name, bases, attrs):
        """Ensure django knows how to act for this model"""
        default_manager = attrs.pop('_default_manager', ServiceManager)
        service_api = attrs.pop('service_api')
        Meta = attrs.pop('Meta')
        klass = super(constructor, cls).__new__(cls, name, basses, attrs)
        klass._default_manager = default_manager(klass, api=service_api)
        klass.objects = klass._default_manager
        klass._meta = Meta()
        return klass

ServiceModel = with_metaclass(constructor, ServiceBaseModel)