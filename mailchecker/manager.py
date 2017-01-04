from oauth2client.file import Storage
from django.conf import settings
from mservice_model.manager import ServiceManager
from mservice_model.queryset import ServiceQuerySet


class ThreadQuerySet(ServiceQuerySet):
    def get(self, *args, **kwargs):
        filter_args = self._get_filter_args(args, kwargs)
        if 'id' not in filter_args:
            raise Exception("No ID found in Thread GET")

        return ThreadQuerySet(
            model=self.model,
            credentials=self.credentials,
            mailer=self.mailer,
            filter_query={'id': filter_args['id']})[0]

    def filter(self, *args, **kwargs):
        filter_args = self._get_filter_args(args, kwargs)
        if 'to__icontains' in filter_args:
            return ThreadQuerySet(
                model=self.model,
                credentials=self.credentials,
                mailer=self.mailer,
                filter_query={'to__icontains': filter_args['to__icontains']})
        # import pdb; pdb.set_trace()
        return self


class MessageQuerySet(ServiceQuerySet):
    def _create(self, frm, to, message_body, thread_id=None):
        return self.mailer.send_message(
            self.credentials, frm, to, message_body, thread_id=thread_id)

    def filter(self, *args, **kwargs):
        filter_args = self._get_filter_args(args, kwargs)
        if 'thread' in filter_args:

            try:
                tid = filter_args['thread'].id
            except AttributeError:
                tid = filter_args['thread']

            return MessageQuerySet(
                model=self.model,
                credentials=self.credentials,
                mailer=self.mailer,
                filter_query={'thread': tid})
        return self

    def get(self, *args, **kwargs):

        filter_args = self._get_filter_args(args, kwargs)
        if 'pk' not in filter_args:
            raise Exception("No PK found in Message GET")

        return MessageQuerySet(
            model=self.model,
            credentials=self.credentials,
            mailer=self.mailer,
            filter_query={'pk': filter_args['pk']})[0]


class GmailManager(ServiceManager):
    def __init__(self, model, **kwargs):
        super(GmailManager, self).__init__(model, **kwargs)
        storage = Storage(settings.CREDENTIALS_PATH)
        self.credentials = storage.get()

    def get_queryset(self):
        return self.queryset(
            credentials=self.credentials,
            model=self.model,
            mailer=self.mailer,
            filter_query=self.initial_filter_query, )


class ThreadManager(GmailManager):
    queryset = ThreadQuerySet


class MessageManager(GmailManager):
    queryset = MessageQuerySet
