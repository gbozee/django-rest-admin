from django.contrib import admin
from mservice_model.admin import ServiceAdmin
from django.contrib.admin import sites
from .models import TodoItem
from django import forms
# Register your models here.

class TodoItemForm(forms.ModelForm):
    class Meta:
        fields = ['title','completed']

@admin.register(TodoItem)
class TodoItemAdmin(ServiceAdmin):
    list_display = ['pk','title','completed']
    form = TodoItemForm



