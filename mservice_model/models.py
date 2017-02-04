from six import with_metaclass
import inspect
from django.db.models.fields import FieldDoesNotExist
from django.db.models.base import ModelState
from django.apps import apps
from .options import ServiceOptions
from .manager import ServiceManager
from .queryset import ServiceQuerySet

# from .options2 import ServiceOptions


class BaseManager(ServiceManager):
    queryset = ServiceQuerySet


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

        module = attrs.pop('__module__', None)
        new_class = super_new(cls, name, bases, attrs)
        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', ServiceOptions)
        else:
            params = {key:value for key, value in attr_meta.__dict__.items() if not key.startswith('__') and not callable(key)}
            SubClass = type(attr_meta.__name__, (ServiceOptions,), params)
            meta = SubClass
        base_meta = getattr(new_class, '_meta', None)

        app_label = None
        app_config = apps.get_containing_app_config(module)
        if getattr(meta, 'app_label', None) is None:
            if app_config is None:
                raise RuntimeError(
                    "Model class %s.%s doesn't declare an explicit "
                    "app_label and isn't in an application in "
                    "INSTALLED_APPS." % (module, name))
            else:
                app_label = app_config.label
        _service_fields = getattr(meta, '_service_fields',None)
        
        # import pdb
        # pdb.set_trace()
        
        dm = attrs.pop('_default_manager', BaseManager)
        service = attrs.pop('_service_api', None)
        if not _service_fields:
            _service_fields = service.initialize()
            # import ipdb; ipdb.set_trace()
        new_class.add_to_class(
            '_meta', meta(
                meta, app_label=app_label, the_class=new_class,
                _service_fields=_service_fields))

        # import pdb; pdb.set_trace()
        if dm:
            new_class._default_manager = dm(new_class, mailer=service)
            new_class.objects = new_class._default_manager
        
        return new_class

    def add_to_class(cls, name, value):
        # We should call the contribute_to_class method only if it's bound
        if not inspect.isclass(value) and hasattr(value,
                                                  'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class ServiceModel(with_metaclass(constructor)):
    _deferred = False
    _state = ModelState()

    def __unicode__(self):
        return self.id

    def serializable_value(self, field_name):
        try:
            field = self._meta.get_field(field_name)
        except FieldDoesNotExist:
            return getattr(self, field_name)
        return getattr(self, field.attname)

    @property
    def pk(self):
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
        return (
            [],
            [], )

    def _get_pk_val(self):
        return None

    def save(self, *args, **kwargs):
        fields = [a.name for a in self._meta.get_fields()]
        data = {}
        for field in fields:
            data.update({field: getattr(self, field)})
        return self.objects.get_queryset().create(**data)


