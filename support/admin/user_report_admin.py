import html
from django.contrib import admin
from django.http import HttpResponse
import csv
import xlsxwriter
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from io import BytesIO
from xhtml2pdf import pisa
from linux.tasks import send_email_task  # Importando o novo método de envio de e-mail com Celery

@admin.action(description='Exportar usuários para CSV')
def export_users_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email'])
    for user in queryset:
        writer.writerow([user.username, user.email])
    return response

@admin.action(description='Exportar usuários para Excel')
def export_users_xlsx(modeladmin, request, queryset):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    worksheet.write('A1', 'Username')
    worksheet.write('B1', 'Email')

    row = 1
    for user in queryset:
        worksheet.write(row, 0, user.username)
        worksheet.write(row, 1, user.email)
        row += 1

    workbook.close()
    output.seek(0)

    response = HttpResponse(output, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xlsx"'
    return response

@admin.action(description='Exportar usuários para PDF')
def export_users_pdf(modeladmin, request, queryset):
    template_path = 'admin/users_pdf.html'
    context = {'users': queryset}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="users.pdf"'

    # Renderizar o HTML para PDF
    template = render_to_string(template_path, context)
    pisa_status = pisa.CreatePDF(
        template, dest=response
    )

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@admin.action(description='Enviar e-mail de boas-vindas com nova senha')
def send_email_to_users(modeladmin, request, queryset):
    for user in queryset:
        new_password = get_random_string(length=8)
        user.set_password(new_password)
        user.save()

        context = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'password': new_password,
        }

        # Usar o método send_email_task do Celery para enviar o e-mail de forma assíncrona
        send_email_task.delay(
            subject='Bem-vindo ao sistema',
            to_email=user.email,
            template_name='emails/welcome_admin.html',  # Certifique-se de que o template existe
            context=context
        )


class CustomUserReport(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email')
    actions = [export_users_csv, export_users_xlsx, export_users_pdf, send_email_to_users]

# admin.site.unregister(User)
# admin.site.register(User, CustomUserReport)
