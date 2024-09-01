# support/forms/smtp_form.py

from django import forms
from support.models.smtp_model import EmailSettings

class EmailSettingsForm(forms.ModelForm):
    class Meta:
        model = EmailSettings
        fields = '__all__'
