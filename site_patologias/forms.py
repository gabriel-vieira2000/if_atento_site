from django import forms
from .models import Admin

class CadastraAdminForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = '__all__'
