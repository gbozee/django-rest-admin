from django.db import models
from django import forms
from django.db.models.fields.related import cached_property


class AutoField(models.fields.AutoField):
    def to_python(self, value):
        return value


class ForeignKey(models.fields.related.ForeignKey):
    def __init__(self, to, *args, **kwargs):
        super().__init__(to, *args, **kwargs)
        self.to = to
        self.model = to

    @cached_property
    def related_model(self):
        import ipdb

        ipdb.set_trace()
        return super().related_model()


class ListFormField(forms.CharField):
    def to_python(self, value):
        """Normalize data to a list of strings."""
        # Return an empty list if no input was given.
        if not value:
            return []
        return value.split(",")

    def prepare_value(self, value):
        if isinstance(value, list):
            return ",".join(value)
        return value

    def validate(self, value):
        """Check if value consists only of valid emails."""
        # Use the parent's handling of required fields, etc.
        super().validate(value)


class ListField(models.Field):
    "Implements comma-separated storage of lists"

    def __init__(self, separator=",", *args, **kwargs):
        self.separator = separator
        self.internal_type = kwargs.pop("internal_type", "CharField")  # or TextField
        super(ListField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(ListField, self).deconstruct()
        # Only include kwarg if it's not the default
        if self.separator != ",":
            kwargs["separator"] = self.separator
        return name, path, args, kwargs

    def to_python(self, value):
        if isinstance(value, list):
            return value

        if value is None:
            return []

        return value.split(self.separator)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)

        return self.get_prep_value(value)

    def get_prep_value(self, value):
        return ",".join(value)

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {"form_class": ListFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
