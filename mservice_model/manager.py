
class ServiceManager(object):
    mailer = None # The mailer component

    def __init__(self, model, **kwargs):        
        self.model = model
        self.mailer = self.mailer or kwargs.get('service')
        self.initial_filter_query = kwargs.get('initial_filter_query', {})

    def complex_filter(self, filter_obj):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def using(self, *args, **kwargs):
        return self

    def iterator(self):
        return iter(self.get_queryset())

    def all(self):
        return self.get_queryset().all()

    def first(self):
        return self.get_queryset().first()

    def last(self):
        return self.get_queryset().last()

    def count(self):
        queryset = self.get_queryset()
        queryset.all()
        return queryset.total_count

    def filter(self, *args, **kwargs):
        return self.get_queryset().filter(*args, **kwargs)

    def get_queryset(self):
        print(self.mailer)
        return self.queryset(
            model=self.model,
            service=self.mailer,
            filter_query=self.initial_filter_query,
        )

    def get(self, *args, **kwargs):
        return self.get_queryset().get(*args, **kwargs)

    def create(self, **kwargs):
        return self.get_queryset().create(**kwargs)
