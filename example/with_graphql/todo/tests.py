from django.test import TestCase
from .models import TodoItem
# Create your tests here.

class TodoItemTestCase(TestCase):
    def test_can_fetch_all_todos(self):
        result = TodoItem.objects.all()
        self.assertGreater(len(result), 0)
