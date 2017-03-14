# from django.db.models import ForeignKey
# from mservice_model.models import ServiceModel
# from .manager import ThreadManager, MessageManager
# from . import mailer
# from django.db.models.fields import (AutoField, CharField, TextField)
# from mservice_model.options import ServiceOptions


# class GmailAutoField(AutoField):
#     def to_python(self, value):
#         return value


# class Thread(ServiceModel):
#     _default_manager = ThreadManager
#     _service_api = mailer.GmailApi("h")

#     # _meta = ThreadOptions()
#     class Meta(ServiceOptions):
#         _service_fields = {
#             'id': GmailAutoField(),
#             'to': CharField(max_length=200),
#             'number_of_messages': CharField(max_length=200),
#         }

#     def __init__(self, id=None, to=None, number_of_messages=None):
#         self.id = id
#         self.to = to
#         self.number_of_messages = number_of_messages

#     @property
#     def messages(self):
#         return Message.objects.filter(thread=self.id)

#     def __unicode__(self):
#         return "<Thread %s with %s messages>" % (
#             self.id, "???"
#             if self.number_of_messages is None else self.number_of_messages)

#     def __repr__(self):
#         return self.__unicode__()

#     def save(self, *args, **kwargs):
#         pass


# class Message(ServiceModel):
#     _default_manager = MessageManager
#     _service_api = mailer

#     class Meta(ServiceOptions):
#         _service_fields = {
#             'id': GmailAutoField(),
#             'receiver': CharField(max_length=200),
#             'sender': CharField(max_length=200),
#             'snippet': CharField(max_length=200),
#             'body': TextField(),
#         }
#         # def additional_bind(self):
#         #     # from .models import Thread, Message
#         #     # self.thread = ForeignKey(Thread)
#         #     # self.thread.contribute_to_class(Thread, 'thread')
#         #     # self.concrete_model = Message
#         #     # self._service_other_fields['thread'] = self.thread

#     def __init__(self,
#                  id=None,
#                  receiver=None,
#                  sender=None,
#                  snippet=None,
#                  body=None,
#                  thread=None,
#                  thread_id=None):
#         self.id = id
#         self.receiver = receiver
#         self.sender = sender
#         self.snippet = snippet
#         self.body = body
#         self.thread_id = thread_id

#         from django.utils.encoding import smart_text
#         if self.body:
#             self.body = smart_text(self.body)
#         if self.snippet:
#             self.snippet = smart_text(self.snippet)

#     @property
#     def thread(self):
#         # return Thread.objects.get(id=self.thread_id)
#         return Thread.objects.get(id=self.id)

#     @thread.setter
#     def thread(self, value):
#         self.thread_id = value.id

#     def __unicode__(self):
#         from django.utils.encoding import smart_text
#         # return smart_text("<Message %s: '%s..'>" % (self.id,
#         # self.snippet[:30]))
#         return smart_text("<Message %s>" % self.id)

#     def __repr__(self):
#         return self.__unicode__()

#     def save(self, *args, **kwargs):

#         # Messages already save do not need re-sending
#         if self.id:
#             return

#         # Send message and fetch ID
#         result = self.objects.get_queryset()._create(
#             frm=self.sender,
#             to=self.receiver,
#             message_body=self.body,
#             thread_id=self.thread_id)

#         # Not all results are returned from the API, re-pull and set
#         # all fields (basically, reassigning the entire instance)
#         new_instance = self.objects.get(pk=result['id'])
#         for field_name in (f.name for f in self._meta.get_fields()):
#             setattr(self, field_name, getattr(new_instance, field_name))


# # Thread._meta._bind()
# # Message._meta._bind()
