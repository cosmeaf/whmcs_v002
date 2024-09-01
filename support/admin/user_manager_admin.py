import pandas as pd
import unicodedata
import re
import csv
import uuid
from django.contrib import admin
from django.utils.text import slugify
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from support.tasks import process_user_creation


# Função para normalizar o nome do projeto
def normalize_projeto(projeto):
    nfkd_form = unicodedata.normalize('NFKD', projeto)
    projeto_sem_acento = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
    projeto_normalizado = re.sub(r'[^a-zA-Z0-9]', '', projeto_sem_acento)
    return projeto_normalizado.lower()

# Função para gerar o username
def gerar_username(nome_completo):
    nomes = nome_completo.split()
    if len(nomes) < 2:
        username = nomes[0].lower()
    else:
        username = nomes[0].lower() + nomes[-1][0].lower() + nomes[1][0].lower()
    return slugify(username)

# Função para verificar se o username já existe e gerar um único
def gerar_username_unico(nome_completo):
    UserModel = get_user_model()
    base_username = gerar_username(nome_completo)
    username = base_username
    counter = 1

    while UserModel.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    return username

# Função para gerar senha
def password_generate():
    return str(uuid.uuid4())[:8]  # Gera uma senha de 8 caracteres

class UserManagerAdmin(admin.ModelAdmin):
    change_list_template = "admin/upload_excel.html"
    list_display = ['__str__']

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('upload-planilha/', self.admin_site.admin_view(self.upload_planilha), name="upload_planilha"),
            path('adicionar-manual/', self.admin_site.admin_view(self.adicionar_manual), name="adicionar_manual"),
            path('exportar-usuarios/', self.admin_site.admin_view(self.exportar_usuarios), name="exportar_usuarios"),
        ]
        return custom_urls + urls


    def upload_planilha(self, request):
        if request.method == "POST":
            if 'excel_file' in request.FILES:
                excel_file = request.FILES["excel_file"]
                df = pd.read_excel(excel_file)

                expected_columns = {
                    'aluno': ['aluno', 'Aluno', 'ALUNO', 'aLuno'],
                    'email': ['email', 'Email', 'E-mail', 'eMail', 'EMAIL'],
                    'projeto': ['projeto', 'Projeto', 'PROJETO']
                }

                def find_column(possibilities, columns):
                    for possibility in possibilities:
                        if possibility in columns:
                            return possibility
                    return None

                aluno_column = find_column(expected_columns['aluno'], df.columns)
                email_column = find_column(expected_columns['email'], df.columns)
                projeto_column = find_column(expected_columns['projeto'], df.columns)

                if not aluno_column or not email_column or not projeto_column:
                    missing_columns = []
                    if not aluno_column:
                        missing_columns.append('aluno')
                    if not email_column:
                        missing_columns.append('email')
                    if not projeto_column:
                        missing_columns.append('projeto')

                    messages.error(request, f"Colunas ausentes na planilha: {', '.join(missing_columns)}")
                    return redirect('admin:upload_planilha')

                data = []
                for index, row in df.iterrows():
                    nome_completo = row[aluno_column]
                    email = row[email_column]

                    username = gerar_username_unico(nome_completo)  # Gera um username único
                    password = password_generate()  # Gera a senha

                    nome_split = nome_completo.split(' ')
                    first_name = nome_split[0]
                    last_name = nome_split[-1]

                    data.append({
                        'nome_completo': nome_completo,
                        'email': email,
                        'username': username,
                        'password': password,
                        'first_name': first_name,
                        'last_name': last_name,
                    })

                # Chamar a tarefa Celery
                task = process_user_creation.delay(data)

                messages.success(request, "A tarefa de criação de usuários foi iniciada. Verifique mais tarde os resultados.")
                return redirect('admin:upload_planilha')
            else:
                messages.error(request, "Por favor, selecione um arquivo Excel.")
        return render(request, "admin/upload_excel.html")



    def adicionar_manual(self, request):
        if request.method == "POST":
            nome_completo = request.POST.get('nome_completo')
            email = request.POST.get('email')

            if nome_completo and email:
                username = gerar_username_unico(nome_completo)  # Gera um username único
                password = password_generate()

                nome_split = nome_completo.split(' ')
                first_name = nome_split[0]
                last_name = nome_split[-1]

                # Criar o usuário no Django
                user = get_user_model().objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                )

                generated_users = request.session.get('generated_users', [])
                generated_users.append({
                    'first_name': first_name,
                    'last_name': last_name,
                    'username': username,
                    'email': email,
                    'password': password
                })
                request.session['generated_users'] = generated_users

                messages.success(request, f"Usuário {username} criado com sucesso.")
                return redirect('admin:upload_planilha')
            else:
                messages.error(request, "Nome completo e e-mail são obrigatórios.")
                return redirect('admin:upload_planilha')

    def exportar_usuarios(self, request):
        generated_users = request.session.get('generated_users', [])

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="generated_users.csv"'

        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Username', 'Email', 'Password'])

        for user in generated_users:
            writer.writerow([user['first_name'], user['last_name'], user['username'], user['email'], user['password']])

        return response