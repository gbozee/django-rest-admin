from django.contrib import admin

from .models import Thread, Message
from .forms import MessageForm, MessageInlineForm


class MessageInline(admin.TabularInline):
    model = Message
    form = MessageInlineForm


class BaseAdmin(admin.ModelAdmin):
    list_per_page = 10
    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        from django.contrib.admin.views.main import ChangeList
        return ChangeList


class MessageAdmin(BaseAdmin):
    ordering = ('id', )
    model = Message
    form = MessageForm


class ThreadAdmin(BaseAdmin):
    # inlines = [
    #     MessageInline,
    # ]
    fields = ('number_of_messages', )
    list_display = ('id', 'to', 'number_of_messages')
    search_fields = ('id', )
    ordering = ('id', )


admin.site.register([Thread], ThreadAdmin)
admin.site.register([Message], MessageAdmin)
