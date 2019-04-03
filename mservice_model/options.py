from django.db.models.fields import (AutoField, CharField, FieldDoesNotExist,
                                     TextField)
from django.db.models import ForeignKey
from django.utils.functional import cached_property
from django.utils.datastructures import ImmutableList, OrderedSet
from django.apps import apps
from .exceptions import ServiceException
IMMUTABLE_WARNING = (
    "The return type of '%s' should never be mutated. If you want to manipulate this list "
    "for your own use, make a copy first.")


def make_immutable_fields_list(name, data):
    return ImmutableList(data, warning=IMMUTABLE_WARNING % name)


class CachedPropertiesMixin(object):

    @cached_property
    def fields(self):
        """
        Returns a list of all forward fields on the model and its parents,
        excluding ManyToManyFields.

        Private API intended only to be used by Django itself; get_fields()
        combined with filtering of field properties is the public API for
        obtaining this field list.
        """
        # For legacy reasons, the fields property should only contain forward
        # fields that are not virtual or with a m2m cardinality. Therefore we
        # pass these three filters as filters to the generator.
        # The third lambda is a longwinded way of checking f.related_model - we don't
        # use that property directly because related_model is a cached property,
        # and all the models may not have been loaded yet; we don't want to cache
        # the string reference to the related_model.
        is_not_an_m2m_field = lambda f: not (f.is_relation and f.many_to_many)
        is_not_a_generic_relation = lambda f: not (
            f.is_relation and f.one_to_many)
        def is_not_a_generic_foreign_key(f):
            return not (
                f.is_relation and f.many_to_one and not (hasattr(f.remote_field, 'model') and f.remote_field.model)
            )

        # is_not_a_generic_foreign_key = lambda f: not (
        #     f.is_relation and f.many_to_one and not (hasattr(f.rel, 'to') and f.rel.to))
        return make_immutable_fields_list(
            "fields", (f for f in self._get_fields(reverse=False)
                       if is_not_an_m2m_field(f) and is_not_a_generic_relation(
                           f) and is_not_a_generic_foreign_key(f)))

    @cached_property
    def concrete_fields(self):
        """
        Returns a list of all concrete fields on the model and its parents.

        Private API intended only to be used by Django itself; get_fields()
        combined with filtering of field properties is the public API for
        obtaining this field list.
        """
        return make_immutable_fields_list("concrete_fields",
                                              (f for f in self.fields
                                               if f.concrete))

    @cached_property
    def local_concrete_fields(self):
        """
        Returns a list of all concrete fields on the model.

        Private API intended only to be used by Django itself; get_fields()
        combined with filtering of field properties is the public API for
        obtaining this field list.
        """
        return make_immutable_fields_list("local_concrete_fields",
                                          (f for f in self.local_fields
                                           if f.concrete))

    # @raise_deprecation(suggested_alternative="get_fields()")
    def get_fields_with_model(self):
        return [self._map_model(f) for f in self.get_fields()]

    # @raise_deprecation(suggested_alternative="get_fields()")
    def get_concrete_fields_with_model(self):
        return [self._map_model(f) for f in self.concrete_fields]

    @cached_property
    def many_to_many(self):
        """
        Returns a list of all many to many fields on the model and its parents.

        Private API intended only to be used by Django itself; get_fields()
        combined with filtering of field properties is the public API for
        obtaining this list.
        """
        return make_immutable_fields_list(
            "many_to_many", (f for f in self._get_fields(reverse=False)
                             if f.is_relation and f.many_to_many))

    @cached_property
    def related_objects(self):
        """
        Returns all related objects pointing to the current model. The related
        objects can come from a one-to-one, one-to-many, or many-to-many field
        relation type.

        Private API intended only to be used by Django itself; get_fields()
        combined with filtering of field properties is the public API for
        obtaining this field list.
        """
        all_related_fields = self._get_fields(
            forward=False, reverse=True, include_hidden=True)
        return make_immutable_fields_list("related_objects", (
            obj for obj in all_related_fields
            if not obj.hidden or obj.field.many_to_many))

    @cached_property
    def _forward_fields_map(self):
        res = {}
        fields = self._get_fields(reverse=False)
        for field in fields:
            res[field.name] = field
            # Due to the way Django's internals work, get_field() should also
            # be able to fetch a field by attname. In the case of a concrete
            # field with relation, includes the *_id name too
            try:
                res[field.attname] = field
            except AttributeError:
                pass
        return res



class ServiceOptions(CachedPropertiesMixin):
    FORWARD_PROPERTIES = {
        'fields', 'many_to_many', 'concrete_fields', 'local_concrete_fields',
        '_forward_fields_map', 'managers', 'managers_map', 'base_manager',
        'default_manager',
    }
    REVERSE_PROPERTIES = {'related_objects', 'fields_map', '_relation_tree'}

    has_auto_field = True
    auto_created = False
    abstract = False
    swapped = False
    virtual_fields = []
    apps = apps
    _service_pk_fields = 'id'
    related_fkey_lookups = []
    default_related_name = None,

    def __init__(self, meta, **kwargs):
        self.meta = meta
        self._service_other_fields = {}
        self.app_label = kwargs.get('app_label', None)
        self._service_fields = kwargs.get('_service_fields', {})
        model_name = kwargs.get('the_class', None)
        # import ipdb; ipdb.set_trace()
        if model_name:
            self.model_name = model_name.__name__
            if not hasattr(self, 'verbose_name'):
                self.verbose_name = self.model_name
            self.verbose_name_plural = self.verbose_name + 's'
            # import ipdb; ipdb.set_trace()
            self.verbose_name_raw = self.model_name
            self.object_name = self.model_name.lower()
            # print(self.model_name)
        self.local_fields = []
        self.private_fields = []

    def add_field(self, field, private=False):
         # Insert the given field in the order in which it was created, using
        # the "creation_counter" attribute of the field.
        # Move many-to-many related fields from self.fields into
        # self.many_to_many.
        if private:
            self.private_fields.append(field)
        elif field.is_relation and field.many_to_many:
            self.local_many_to_many.insert(bisect(self.local_many_to_many, field), field)
        else:
            self.local_fields.insert(bisect(self.local_fields, field), field)
            self.setup_pk(field)

        # If the field being added is a relation to another known field,
        # expire the cache on this field and the forward cache on the field
        # being referenced, because there will be new relationships in the
        # cache. Otherwise, expire the cache of references *to* this field.
        # The mechanism for getting at the related model is slightly odd -
        # ideally, we'd just ask for field.related_model. However, related_model
        # is a cached property, and all the models haven't been loaded yet, so
        # we need to make sure we don't cache a string reference.
        if field.is_relation and hasattr(field.remote_field, 'model') and field.remote_field.model:
            try:
                field.remote_field.model._meta._expire_cache(forward=False)
            except AttributeError:
                pass
            self._expire_cache()
        else:
            self._expire_cache(reverse=False)

    def _bind(self):
        for field_name, field in self._service_fields.items():
            setattr(self, field_name, field)
            field.set_attributes_from_name(field_name)
        try:
            self.pk = self._service_fields[self._service_pk_fields]
        except KeyError:
            raise ServiceException("Did you forget to add an `id` model field?")
        self.additional_bind()

    def additional_bind(self):
        pass

    def get_fields(self, **kwargs):
        return self._get_fields()

    def _get_fields(self, reverse=True, forward=True):
        return tuple(field
                     for field_name, field in sorted(
                         list(self._service_fields.items()) + list(
                             self._service_other_fields.items())))

    def get_field(self, field_name):
        try:
            return self._service_fields[field_name]
        except KeyError:
            try:
                return self._service_other_fields[field_name]
            except KeyError:
                raise FieldDoesNotExist()

    @property
    def app_config(self):
        # Don't go through get_app_config to avoid triggering imports.
        return self.apps.app_configs.get(self.app_label)
