from django.db import models
from django.contrib.auth.models import User
from rest_framework import serializers


# Create your models here.
class TodoItem(models.Model):
    title = models.TextField()
    completed = models.BooleanField(default=False)
    owner = models.ForeignKey(User, null=True, related_name='todos')

    def __repr__(self):
        return "<TodoItem %s>" % self.title
        

class TodoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoItem
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'