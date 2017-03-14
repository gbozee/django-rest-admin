# pylint: disable=E1101
from django.shortcuts import render
from collections import OrderedDict
from django.db import models
from rest_framework import viewsets, routers, pagination
from rest_framework_filters.backends import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
import rest_framework_filters as filters
from rest_framework.response import Response
from .models import User, UserSerializer, TodoItem, TodoItemSerializer


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data, queryset, field):
        last_record = queryset.last()
        first_record = queryset.first()
        response = OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('last_id', last_record.pk),
            ('first_id', first_record.pk),
            ('results', data),
        ])
        if field:
            date_range = queryset.aggregate(
                first=models.Min(field), last=models.Max(field))
            response['date_range'] = date_range
        return Response(response)

class BaseViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    ordering_fields = '__all__'

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        field_name = self.request.query_params.get('field_name')
        filted_query = self.filter_queryset(self.get_queryset())
        return self.paginator.get_paginated_response(data, filted_query, field_name)

class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TodoItemViewSet(BaseViewSet):
    queryset = TodoItem.objects.all()
    serializer_class = TodoItemSerializer


router = routers.DefaultRouter()
router.register(r'todos', TodoItemViewSet)
router.register(r'users', UserViewSet)