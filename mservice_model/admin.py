from django.contrib import admin

from django.core.paginator import Paginator, Page
from django.utils.functional import cached_property


class ServicePage(Page):
    pass


class ServicePaginator(Paginator):
    @property
    def count(self):
        """
        Returns the total number of objects, across all pages.
        """
        # import ipdb; ipdb.set_trace()
        try:
            self.object_list.get_data()
            return self.object_list.total_count
        except (AttributeError, TypeError):
            # AttributeError if object_list has no count() method.
            # TypeError if object_list.count() requires arguments
            # (i.e. is of type list).
            return len(self.object_list)

    def page(self, number):
        """
        Returns a Page object for the given 1-based page number.
        """
        number = self.validate_number(number)
        new_object_list = self.object_list._get_data(
            page=number, per_page=self.per_page)
        return self._get_page(new_object_list, number, self)


class ServiceAdmin(admin.ModelAdmin):
    list_per_page = 100
    paginator = ServicePaginator
