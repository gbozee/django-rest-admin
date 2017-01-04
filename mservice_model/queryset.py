class GmailQuery(object):
    select_related = False
    order_by = tuple()


class ServiceQuerySet(object):
    """Generic queryset for services fetched over a remote api"""

    def using(self, db):
        return self

    def __init__(self, *args, **kwargs):
        self._cache = None
        self.total_count = 0
        self.ordered = True
        self.model = kwargs.pop('model')
        self.credentials = kwargs.pop('credentials')
        self.mailer = kwargs.pop('mailer', None)
        self.filter_query = kwargs.pop('filter_query', {})
        self.query = GmailQuery()

    def order_by(self, *args, **kwargs):
        return self

    def none(self, *args, **kwargs):
        cloned_query = self._clone()
        cloned_query.filter_query = {}
        return cloned_query

    def _clone(self, *args, **kwargs):
        return self.__class__(
            model=self.model,
            credentials=self.credentials,
            mailer=self.mailer,
            filter_query=self.filter_query)

    def count(self):
        return len(self._get_data())

    def __getitem__(self, k):
        return self._get_data()[k]

    def __repr__(self):
        return repr(self._get_data())

    def __iter__(self):
        return iter(self._get_data())

    def all(self):
        return self._get_data()

    def _set_model_attrs(self, instance):
        instance._meta = self.model._meta
        instance._state = self.model._state
        return instance

    def _get_filter_args(self, args, kwargs):
        filter_args = kwargs if kwargs else {}
        if len(args) > 0:
            filter_args.update(dict(args[0].children))
        return filter_args

    def __len__(self):
        return len(self._get_data())

    def _get_data(self, **kwargs):
        """Get the query from the service api.
        register all the possible queries. in this cas
        field_query = ['id', 'to_contains']"""
        if not self._cache:
            messages, self.total_count = self.mailer.get_data(
                self.credentials, self.filter_query, cls=self.model, **kwargs)
            self._cache = [
                self._set_model_attrs(instance) for instance in messages
            ]
            # self._cache = map(self._set_model_attrs, all_threads)

        return self._cache
