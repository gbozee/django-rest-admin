from django import forms


class ServiceForm(forms.ModelForm):
    # available_days = ListFormField(required=False)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for x in self.fields.keys():
            self.fields[x].required = False