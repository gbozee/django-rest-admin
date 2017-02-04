from django.contrib import admin
from mservice_model.admin import ServiceAdmin
# Register your models here.
from .models import BaseRequestTutor
from .forms import BaseRequestTutorForm

class GenderFilter(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        return

@admin.register(BaseRequestTutor)
class ParentRequestAdmin(ServiceAdmin):
    list_display = ('first_name', 'last_name', 'email')
    form = BaseRequestTutorForm
    date_hierarchy  = 'modified'
    search_fields = ('^email',)
    list_filter = ('gender',)