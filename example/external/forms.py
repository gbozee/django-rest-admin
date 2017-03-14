from mservice_model.forms import ServiceForm
from .models import BaseRequestTutor

class BaseRequestTutorForm(ServiceForm):
    # available_days = ListFormField(required=False)
    class Meta:
        model = BaseRequestTutor
        fields = '__all__'