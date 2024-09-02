import os
from django.contrib.auth.models import User
from django.shortcuts import render

def home_view(request):
    projects = []
    members_base_path = '/var/www/members'
    home_base_path = '/home'

    # Itera sobre os itens no diretório base
    for folder_name in os.listdir(members_base_path):
        project_path = os.path.join(members_base_path, folder_name)

        # Verifica se é uma pasta e se ela existe
        if os.path.isdir(project_path):
            # Itera sobre todos os usuários para encontrar o dono do projeto
            for user in User.objects.all():
                user_home_path = os.path.join(home_base_path, user.username)
                user_project_path = os.path.join(user_home_path, folder_name)

                # Verifica se a pasta do projeto está dentro do diretório do usuário
                if os.path.isdir(user_project_path):
                    author_name = f'{user.first_name} {user.last_name}'
                    projects.append({
                        'folder_name': folder_name,
                        'author_name': author_name,
                        'logo_url': 'https://framerusercontent.com/images/TG6WAjlT9X9sEq6evGgBkyhOYk.png',
                        'project_url': f'https://{folder_name}.{request.get_host()}'
                    })
                    break

    context = {
        'projects': projects
    }
    return render(request, 'index.html', context)
