from django.contrib import admin
from mservice_model.admin import ServiceAdmin
# Register your models here.
from .models import BaseRequestTutor
from .forms import BaseRequestTutorForm

@admin.register(BaseRequestTutor)
class ParentRequestAdmin(ServiceAdmin):
    list_display = ('first_name', 'last_name')
    form = BaseRequestTutorForm
    date_hierarchy  = 'modified'
    