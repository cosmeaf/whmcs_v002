from django import forms
from django.contrib import admin, messages
from django.core.mail import send_mail, get_connection
from django.shortcuts import render, redirect
from django.urls import path
from support.models.smtp_model import EmailSettings

# Formulário para capturar o e-mail do usuário
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
                email_settings = EmailSettings.objects.first()
                if not email_settings:
                    self.message_user(request, "No email settings found.", level=messages.ERROR)
                    return redirect('..')

                try:
                    connection = get_connection(
                        backend=email_settings.email_backend,
                        host=email_settings.email_host,
                        port=email_settings.email_port,
                        username=email_settings.email_host_user,
                        password=email_settings.email_host_password,
                        use_tls=email_settings.email_use_tls
                    )
                    send_mail(
                        'Test Email',
                        'This is a test email.',
                        email_settings.default_from_email,
                        [test_email],  # Usando o e-mail fornecido pelo usuário
                        connection=connection
                    )
                    self.message_user(request, f"Test email sent successfully to {test_email}.", level=messages.SUCCESS)
                except Exception as e:
                    self.message_user(request, f"Error sending test email: {e}", level=messages.ERROR)
                return redirect('..')
        else:
            form = EmailTestForm()

        return render(request, 'admin/test_email_form.html', {'form': form})
