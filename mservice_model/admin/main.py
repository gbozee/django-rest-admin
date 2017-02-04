from django.contrib.admin.views.main import ChangeList
from django.core.paginator import InvalidPage
from django.contrib.admin.options import (
    IS_POPUP_VAR,
    TO_FIELD_VAR,
    IncorrectLookupParameters, )


class ServiceChangeList(ChangeList):
    def get_results(self, request):
        paginator = self.model_admin.get_paginator(request, self.queryset,
                                                   self.list_per_page)
        # Get the number of objects, with admin filters applied.
        # import ipdb; ipdb.set_trace()
        
        result_count = paginator.count
        # import pdb; pdb.set_trace()
        # Get the total number of objects, with no admin filters applied.
        if self.model_admin.show_full_result_count:
            self.root_queryset.count()
            full_result_count = self.root_queryset.total_count
        else:
            full_result_count = None
        # import ipdb; ipdb.set_trace()
        can_show_all = result_count <= self.list_max_show_all
        multi_page = result_count > self.list_per_page

        # Get the list of objects to display on this page.
        if (self.show_all and can_show_all) or not multi_page:
            result_list = self.queryset._clone()
        else:
            try:
                result_list = paginator.page(self.page_num + 1).object_list
            except InvalidPage:
                raise IncorrectLookupParameters

        self.result_count = result_count
        self.show_full_result_count = self.model_admin.show_full_result_count
        # Admin actions are shown if there is at least one entry
        # or if entries are not counted because show_full_result_count is disabled
        self.show_admin_actions = not self.show_full_result_count or bool(
            full_result_count)
        self.full_result_count = full_result_count
        self.result_list = result_list
        self.can_show_all = can_show_all
        self.multi_page = multi_page
        self.paginator = paginator
