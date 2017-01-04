from django.utils.functional import cached_property


IMMUTABLE_WARNING = (
    "The return type of '%s' should never be mutated. If you want to manipulate this list "
    "for your own use, make a copy first."
)

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
        is_not_a_generic_foreign_key = lambda f: not (
            f.is_relation and f.many_to_one and not (
                hasattr(f.rel, 'to') and f.rel.to)
        )
        return make_immutable_fields_list(
            "fields",
            (f for f in self._get_fields(reverse=False) if
             is_not_an_m2m_field(f) and is_not_a_generic_relation(f)
             and is_not_a_generic_foreign_key(f))
        )

    @cached_property
    def concrete_fields(self):
        """
        Returns a list of all concrete fields on the model and its parents.

        Private API intended only to be used by Django itself; get_fields()
        combined with filtering of field properties is the public API for
        obtaining this field list.
        """
        try:
            return make_immutable_fields_list(
                "concrete_fields", (f for f in self.fields if f.concrete)
            )
        except AttributeError:
            import ipdb
            ipdb.set_trace()

    @cached_property
    def local_concrete_fields(self):
        """
        Returns a list of all concrete fields on the model.

        Private API intended only to be used by Django itself; get_fields()
        combined with filtering of field properties is the public API for
        obtaining this field list.
        """
        return make_immutable_fields_list(
            "local_concrete_fields", (f for f in self.local_fields if f.concrete)
        )

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
            "many_to_many",
            (f for f in self._get_fields(reverse=False)
             if f.is_relation and f.many_to_many)
        )

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
        return make_immutable_fields_list(
            "related_objects",
            (obj for obj in all_related_fields
             if not obj.hidden or obj.field.many_to_many)
        )
