from .base import GmailModel
from .manager import MessageManager
from .options import MessageOptions, ForeignKey


class Message(GmailModel):
    _default_manager = MessageManager

    # _meta = MessageOptions()
    class Meta(MessageOptions):
        def additional_bind(self):
            from .models import Thread
            self.thread = ForeignKey(Thread)
            self.thread.contribute_to_class(Thread, 'thread')
            self.concrete_model = Message
            self._service_other_fields['thread'] = self.thread

    def __init__(self,
                 id=None,
                 receiver=None,
                 sender=None,
                 snippet=None,
                 body=None,
                 thread=None,
                 thread_id=None):
        self.id = id
        self.receiver = receiver
        self.sender = sender
        self.snippet = snippet
        self.body = body
        self.thread_id = thread_id

        from django.utils.encoding import smart_text
        if self.body:
            self.body = smart_text(self.body)
        if self.snippet:
            self.snippet = smart_text(self.snippet)

    @property
    def thread(self):
        from .models import Thread
        # return Thread.objects.get(id=self.thread_id)
        return Thread.objects.get(id=self.id)

    @thread.setter
    def thread(self, value):
        self.thread_id = value.id

    def __unicode__(self):
        from django.utils.encoding import smart_text
        # return smart_text("<Message %s: '%s..'>" % (self.id,
        # self.snippet[:30]))
        return smart_text("<Message %s>" % self.id)

    def __repr__(self):
        return self.__unicode__()

    def save(self, *args, **kwargs):

        # Messages already save do not need re-sending
        if self.id:
            return

        # Send message and fetch ID
        result = self._default_manager.get_queryset()._create(
            frm=self.sender,
            to=self.receiver,
            message_body=self.body,
            thread_id=self.thread_id)

        # Not all results are returned from the API, re-pull and set
        # all fields (basically, reassigning the entire instance)
        new_instance = self._default_manager.get(pk=result['id'])
        for field_name in (f.name for f in self._meta.get_fields()):
            setattr(self, field_name, getattr(new_instance, field_name))


Message._meta._bind()
