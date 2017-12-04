from mservice_model.models import ServiceModel, model_factory
from .api import instance as todo_api
# Create your models here.

class Mixin(object):
    def __repr__(self):
        return "<TodoItem %s>" % self.id

class TodoItem(ServiceModel):
    _service_api = todo_api

    class Meta:
        ordering = ('id',)
        verbose_name = "Todo Item"

# TodoItem = model_factory(todo_api, "TodoItem", base_class=Mixin)

    
