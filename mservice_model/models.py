from six import with_metaclass
import inspect
from django.db.models.fields import FieldDoesNotExist
from django.db.models.base import ModelState
from django.apps import apps
from .options import ServiceOptions
from .manager import ServiceManager
from .queryset import ServiceQuerySet
from django.forms import modelform_factory

# from .options2 import ServiceOptions


class BaseManager(ServiceManager):
    queryset = ServiceQuerySet


def _has_contribute_to_class(value):
    # Only call contribute_to_class() if it's bound.
    return not inspect.isclass(value) and hasattr(value, "contribute_to_class")


class constructor(type):
    def __init__(cls, name, bases, clsdict):
        if len(cls.mro()) > 2:
            cls._meta._bind()
        super().__init__(name, bases, clsdict)

    def __new__(cls, name, bases, attrs):
        super_new = super(constructor, cls).__new__
        parents = [b for b in bases if isinstance(b, constructor)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        module = attrs.pop("__module__", None)
        new_attrs = {"__module__": module}
        contributable_attrs = {}
        for obj_name, obj in list(attrs.items()):
            if _has_contribute_to_class(obj):
                contributable_attrs[obj_name] = obj
            else:
                new_attrs[obj_name] = obj

        new_class = super_new(cls, name, bases, new_attrs)
        attr_meta = attrs.pop("Meta", None)
        if not attr_meta:
            meta = getattr(new_class, "Meta", ServiceOptions)
        else:
            params = {
                key: value
                for key, value in attr_meta.__dict__.items()
                if not key.startswith("__") and not callable(key)
            }
            SubClass = type(attr_meta.__name__, (ServiceOptions,), params)
            meta = SubClass
        base_meta = getattr(new_class, "_meta", None)

        app_label = None
        app_config = apps.get_containing_app_config(module)
        if getattr(meta, "app_label", None) is None:
            if app_config is None:
                raise RuntimeError(
                    "Model class %s.%s doesn't declare an explicit "
                    "app_label and isn't in an application in "
                    "INSTALLED_APPS." % (module, name)
                )
            else:
                app_label = app_config.label
        _service_fields = getattr(meta, "_service_fields", contributable_attrs)
        # import ipdb; ipdb.set_trace()

        # import pdb
        # pdb.set_trace()

        dm = attrs.pop("_default_manager", BaseManager)
        service = attrs.pop("_service_api", None)
        if not _service_fields:
            _service_fields = service.initialize()
            # import ipdb; ipdb.set_trace()
        new_class.add_to_class(
            "_meta",
            meta(
                meta,
                app_label=app_label,
                the_class=new_class,
                _service_fields=_service_fields,
            ),
        )
        # import pdb; pdb.set_trace()
        if dm:
            new_class._default_manager = dm(new_class, service=service)
            new_class.objects = new_class._default_manager
        

        return new_class

    def add_to_class(cls, name, value):
        # We should call the contribute_to_class method only if it's bound
        if _has_contribute_to_class(value):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class ServiceModel(with_metaclass(constructor)):
    _deferred = False
    _state = ModelState()

    def __str__(self):
        return str(self.id)

    def serializable_value(self, field_name):
        try:
            field = self._meta.get_field(field_name)
        except FieldDoesNotExist:
            return getattr(self, field_name)
        return getattr(self, field.attname)

    @property
    def pk(self):
        if hasattr(self, "id"):
            return self.id
        self.id = None
        return self.id

        # klass.objects = klass._default_manager

    def __eq__(self, other):
        if isinstance(other, ServiceModel):
            return self.pk == other.pk
        return False

    def full_clean(self, *args, **kwargs):
        pass

    def validate_unique(self, *args, **kwargs):
        pass

    def _get_unique_checks(self, *args, **kwargs):
        return ([], [])

    def _get_pk_val(self):
        return None

    def save(self, *args, **kwargs):
        fields = [a.name for a in self._meta.get_fields()]
        data = {}
        for field in fields:
            data.update({field: getattr(self, field, None)})
        result = self.objects.get_queryset().create(**data)
        for key in fields:
            setattr(self, key, getattr(result, key, None))
        return self

    def __init__(self, **kwargs):
        self.id = None
        for key, value in kwargs.items():
            if "_id" in key:
                new_key = key.replace("_id", "")
                models = self._meta._service_fields
                ModelFromForeignKey = models[new_key].model
                setattr(self, new_key, ModelFromForeignKey.objects.get(id=value))
            setattr(self, key, value)

    def __eq__(self, other):
        if not isinstance(other, ServiceModel):
            return False
        my_pk = self.pk
        if my_pk is None:
            return self is other
        return my_pk == other.pk



def model_factory(service, name, base_class=None):
    BaseClass = base_class or object

    class SampleModel(ServiceModel, BaseClass):
        _service_api = service

        class Meta:
            app_label = name.lower()

    SampleModel.__name__ = name
    return SampleModel
