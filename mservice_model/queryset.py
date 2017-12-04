class GmailQuery(object):
    select_related = False
    order_by = tuple()


class ServiceQuerySet(object):
    """Generic queryset for services fetched over a remote api
    total_count is used to get the total counts of objects"""

    def using(self, db):
        return self

    def __init__(self, *args, **kwargs):
        self._cache = None
        self.total_count = 0
        self.ordered = True
        self.model = kwargs.pop('model')
        self.mailer = kwargs.pop('mailer', None)
        self.filter_query = kwargs.pop('filter_query', {})
        self.query = GmailQuery()
        self.order_dict = ()

    def order_by(self, *args, **kwargs):
        self.order_dict = args
        self._cache = None
        self._get_data()
        return self

    def aggregate(self, **kwargs):
        if self.date_range:
            return self.date_range
        return self.mailer.aggregate(**kwargs)

    def none(self, *args, **kwargs):
        cloned_query = self._clone()
        cloned_query.filter_query = {}
        return cloned_query

    def _variables(self):
        return dict(model=self.model,
        mailer=self.mailer,
        filter_query=self.filter_query)

    def _clone(self, *args, **kwargs):
        return self.__class__(**self._variables(), **kwargs)
        
    def first(self):
        return self[0]

    def last(self):
        return self[-1]

    def count(self):
        return len(self._get_data())

    def get(self, *args, **kwargs):
        filter_args = self._get_filter_args(args, kwargs)
        if 'id' not in filter_args:
            raise Exception("No ID found in Thread GET")
        params = self._variables()
        params.update(filter_query={'id': filter_args['id']})
        return ServiceQuerySet(**params)[0]

    def filter(self, *args, **kwargs):
        """Implement the filter function on the queryset"""
        filter_args = self._get_filter_args(args, kwargs)
        if filter_args:
            params = self._variables()
            params.update(filter_query=filter_args)
            return ServiceQuerySet(**params)
        return self

    def create(self, **kwargs):
        data = self.mailer.create(cls=self.model, **kwargs)
        self._cache = [
                self._set_model_attrs(instance) for instance in [data]
            ]
        return self[0]

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

    def params_for_fetching_data(self, **kwargs):
        """parameters to be passed to _get_data function. should BufferError
        overidden by child classes"""
        return dict(filter_by=self.filter_query,order_by=self.order_dict,cls=self.model, **kwargs)

    def _get_data(self, **kwargs):
        """Get the query from the service api.
        register all the possible queries. in this cas
        field_query = ['id', 'to_contains']"""
        # import pdb; pdb.set_trace()
        if kwargs:
            self._cache = None
        if not self._cache:
            messages, self.total_count, self.date_range, self.last_id = self.mailer.get_data(
                **self.params_for_fetching_data(), **kwargs)
            self._cache = [
                self._set_model_attrs(instance) for instance in messages
            ]
            # self._cache = map(self._set_model_attrs, all_threads)

        return self._cache

    def datetimes(self, field_name, kind, order='ASC', tzinfo=None):
        """
        Returns a list of datetime objects representing all available
        datetimes for the given field_name, scoped to 'kind'.
        """
        assert kind in ("year", "month", "day", "hour", "minute", "second"), \
            "'kind' must be one of 'year', 'month', 'day', 'hour', 'minute' or 'second'."
        assert order in ('ASC', 'DESC'), \
            "'order' must be either 'ASC' or 'DESC'."
        return self.mailer.datetimes(field_name, kind, order, self.filter_query)

    def distinct(self):
        return self

    def values_list(self, *args, **kwargs):
        return self.mailer.get_values_list(*args, **kwargs)