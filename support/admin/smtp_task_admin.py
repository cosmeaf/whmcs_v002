# support/admin.py

from django import forms
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
from support.models.smtp_model import EmailSettings
from support.utils.email_sender import EmailSender

class EmailTestForm(forms.Form):
    email = forms.EmailField(label="E-mail para teste", max_length=254, required=True)

@admin.register(EmailSettings)
class EmailSettingsAdmin(admin.ModelAdmin):
    list_display = ['email_backend', 'email_service', 'email_host', 'email_host_user', 'default_from_email']
    change_list_template = 'admin/email_settings_changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('test-email/', self.admin_site.admin_view(self.test_email), name='test-email'),
        ]
        return custom_urls + urls

    def test_email(self, request):
        if request.method == 'POST':
            form = EmailTestForm(request.POST)
            if form.is_valid():
                test_email = form.cleaned_data['email']
                try:
                    email_sender = EmailSender(
                        subject="Test Email",
                        to=test_email
                    )
                    email_sender.send_email()
                    self.message_user(request, f"Test email is being sent to {test_email}.", level=messages.SUCCESS)
                except Exception as e:
                    self.message_user(request, f"Error: {e}", level=messages.ERROR)
                return redirect('..')
        else:
            form = EmailTestForm()

        return render(request, 'admin/test_email_form.html', {'form': form})
