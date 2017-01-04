from django.contrib import admin

from .models import Thread, Message
from .forms import MessageForm, MessageInlineForm
from mservice_model.admin import ServiceAdmin


class MessageInline(admin.TabularInline):
    model = Message
    form = MessageInlineForm


class MessageAdmin(ServiceAdmin):
    ordering = ('id', )
    model = Message
    form = MessageForm


class ThreadAdmin(ServiceAdmin):
    # inlines = [
    #     MessageInline,
    # ]
    fields = ('number_of_messages', )
    list_display = ('id', 'to', 'number_of_messages')
    search_fields = ('id', )
    ordering = ('id', )


admin.site.register([Thread], ThreadAdmin)
admin.site.register([Message], MessageAdmin)
