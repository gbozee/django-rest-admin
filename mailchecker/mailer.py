import base64
import httplib2
from apiclient.discovery import build
from email.mime.text import MIMEText
from mservice_model.api import ServiceApi, Bunch

ME = 'me'


class GmailApi(ServiceApi):
    def get_data(self, credentials, filter_by, cls=Bunch, **kwargs):
        """Returns a tuple of the fetched data and the total count"""
        messages = []
        total = 0
        if cls.__name__ == 'Message':
            if 'pk' in filter_by:
                messages = get_message_by_id(
                    credentials, filter_by['pk'], cls=cls)
            elif not 'thread' in filter_by:
                messages = []
            else:
                messages, total = get_messages_by_thread_id(
                    credentials, filter_by['thread'], cls=cls)

        if cls.__name__ == 'Thread':
            if 'id' in filter_by:
                messages = get_thread_by_id(
                    credentials, filter_by['id'], cls=cls)

            else:
                messages, total = get_all_threads(
                    credentials, filter_by, cls=cls)
                # import ipdb; ipdb.set_trace()
                # Can be a generator instead

        return messages, total


def _get_gmail_service(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('gmail', 'v1', http=http)


def _make_message(msg, cls):
    try:
        parts = [p['body'] for p in msg['payload']['parts']]
    except KeyError:
        parts = [msg['payload']['body']]

    body = ''.join(
        base64.urlsafe_b64decode(p['data'].encode('utf-8')) for p in parts
        if 'data' in p)
    sender = [
        h['value'] for h in msg['payload']['headers']
        if h['name'].lower() in 'from'
    ][0]
    receiver = [
        h['value'] for h in msg['payload']['headers']
        if h['name'].lower() == 'to'
    ][0]
    return cls(id=msg['id'],
               thread_id=msg['threadId'],
               snippet=msg['snippet'],
               receiver=receiver,
               sender=sender,
               body=body)


def send_message(credentials,
                 frm,
                 to,
                 message_body,
                 subject="Hello from Pycon",
                 thread_id=None):
    gmail = _get_gmail_service(credentials)
    message = MIMEText(message_body)
    message['to'] = to
    message['from'] = frm
    message['subject'] = subject

    payload = {'raw': base64.b64encode(message.as_bytes()).decode('utf-8')}
    if thread_id:
        payload['threadId'] = thread_id
    return gmail.users().messages().send(
        userId=ME,
        body=payload, ).execute()


def get_messages_by_thread_id(credentials, thread_id, cls=Bunch):
    gmail = _get_gmail_service(credentials)
    thread = gmail.users().threads().get(userId=ME, id=thread_id).execute()
    import ipdb
    ipdb.set_trace()
    total = 0
    return [_make_message(m, cls) for m in thread['messages']], total


def get_all_threads(credentials, filter_by, cls=Bunch):
    to = (filter_by['to__icontains'] if 'to__icontains' in filter_by else None)

    gmail = _get_gmail_service(credentials)
    params = {'userId': ME, }
    if to:
        params['q'] = 'to:%s' % to
    threads = gmail.users().threads().list(**params).execute()
    total = threads['resultSizeEstimate']
    if not threads or (to != None and threads['resultSizeEstimate'] is 0):
        return tuple(), total
    return tuple(
        cls(id=t['id'], number_of_messages=None, to=None)
        for t in threads['threads']), total


def get_all_messages(credentials, cls=Bunch):
    gmail = _get_gmail_service(credentials)
    messages = gmail.users().messages().list(userId=ME, ).execute()['messages']
    import ipdb
    ipdb.set_trace()
    total = 0
    return [_make_message(m, cls) for m in messages], total


def get_thread_by_id(credentials, thread_id, cls=Bunch):
    gmail = _get_gmail_service(credentials)
    # import pdb; pdb.set_trace()
    thread = gmail.users().threads().get(userId=ME, id=thread_id).execute()
    return [
        cls(id=thread['id'],
            to=None,
            number_of_messages=len(thread['messages']))
    ]


def get_message_by_id(credentials, message_id, cls=Bunch):
    gmail = _get_gmail_service(credentials)
    message = gmail.users().messages().get(userId=ME, id=message_id).execute()
    return [_make_message(message, cls)]
