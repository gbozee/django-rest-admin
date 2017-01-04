from django.db.models.fields import FieldDoesNotExist

class Bunch(object):
    def __init__(self, *args, **kwargs):
        self.__dict__ = kwargs
        self.pk = self.id

    def __unicode__(self):
        return self.id

    def serializable_value(self, field_name):
        try:
            field = self._meta.get_field(field_name)
        except FieldDoesNotExist:
            return getattr(self, field_name)
        return getattr(self, field.attname)


class ServiceApi(object):
    def get_data(self, *args, **kwargs):
        raise NotImplementedError