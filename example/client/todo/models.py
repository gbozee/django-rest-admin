from mservice_model.models import ServiceModel, model_factory
from .api import instance as todo_api
# Create your models here.

class Mixin(object):
    def __repr__(self):
        return "<TodoItem %s>" % self.id

TodoItem = model_factory(todo_api, "TodoItem", base_class=Mixin)

    
