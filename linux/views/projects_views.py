import os
import pwd
import grp
import shutil
import zipfile
import subprocess
import json
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import logging

# Configure logging
logger = logging.getLogger(__name__)


def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

@login_required
def projects(request):
    user_home = os.path.expanduser(f"~{request.user.username}")
    
    files_and_folders = []
    for item in os.listdir(user_home):
        if not item.startswith('.'):
            item_path = os.path.join(user_home, item)
            stats = os.stat(item_path)
            permissions = oct(stats.st_mode)[-3:]
            permission_str = f"{permissions} {pwd.getpwuid(stats.st_uid).pw_name} {grp.getgrgid(stats.st_gid).gr_name}"

            if os.path.isdir(item_path):
                size = get_folder_size(item_path)
            else:
                size = stats.st_size

            files_and_folders.append({
                'name': item,
                'type': 'Folder' if os.path.isdir(item_path) else 'File',
                'size': size if size > 0 else '-',
                'permissions': permission_str,
                'path': os.path.relpath(item_path, user_home),
                'is_zip': item.endswith('.zip')
            })

    context = {
        'files_and_folders': files_and_folders,
    }
    return render(request, 'dashboard/projects.html', context)



@login_required
def project_detail(request, name_project):
    user_home = os.path.expanduser(f"~{request.user.username}")
    project_path = os.path.join(user_home, name_project)
    
    if not os.path.exists(project_path):
        return HttpResponse("Project not found", status=404)

    files_and_folders = []
    for item in os.listdir(project_path):
        item_path = os.path.join(project_path, item)
        stats = os.stat(item_path)
        permissions = oct(stats.st_mode)[-3:]
        permission_str = f"{permissions} {pwd.getpwuid(stats.st_uid).pw_name} {grp.getgrgid(stats.st_gid).gr_name}"

        files_and_folders.append({
            'name': item,
            'type': 'Folder' if os.path.isdir(item_path) else 'File',
            'size': stats.st_size if os.path.isfile(item_path) else '-',  # Corrigir cálculo de tamanho
            'permissions': permission_str,
            'path': os.path.relpath(item_path, user_home),
            'is_file': os.path.isfile(item_path)
        })

    context = {
        'files_and_folders': files_and_folders,
        'current_project': name_project,
    }
    return render(request, 'dashboard/project_detail.html', context)


@login_required
@csrf_exempt
def upload_project(request):
    if request.method == 'POST' and request.FILES['file']:
        user_home = os.path.expanduser(f"~{request.user.username}")
        upload_file = request.FILES['file']
        
        if not os.path.exists(user_home):
            os.makedirs(user_home)
        
        # Salvar o arquivo no diretório home do usuário
        file_path = os.path.join(user_home, upload_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in upload_file.chunks():
                destination.write(chunk)
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'failed', 'message': 'No file uploaded'})


@login_required
@csrf_exempt
def save_file_content(request):
    if request.method == 'POST':
        try:
            # Recebendo o caminho e o conteúdo do arquivo
            file_path = os.path.join(os.path.expanduser(f"~{request.user.username}"), request.POST.get('path'))
            content = request.POST.get('content')

            # Escrevendo o novo conteúdo no arquivo
            with open(file_path, 'w') as file:
                file.write(content)

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'failed', 'message': 'Invalid request method'})



@login_required
@csrf_exempt
@require_POST
def unzip_file(request):
    try:
        # Carrega o JSON do corpo da requisição
        logger.debug(f"Request body: {request.body}")
        data = json.loads(request.body)
        logger.debug(f"Parsed data: {data}")

        zip_filename = data.get('path')
        logger.debug(f"Zip filename: {zip_filename}")

        if not zip_filename:
            logger.error("Invalid file path")
            return JsonResponse({'status': 'error', 'message': 'Invalid file path'})

        # Diretório home do usuário logado
        user_home = f"/home/{request.user.username}"

        # Caminho completo do arquivo .zip
        zip_path = os.path.join(user_home, zip_filename)

        # Verificar se o arquivo existe
        if not os.path.exists(zip_path):
            return JsonResponse({'status': 'error', 'message': 'File not found'})

        # Verificar se o arquivo é um .zip válido
        if not zipfile.is_zipfile(zip_path):
            return JsonResponse({'status': 'error', 'message': 'The file is not a valid .zip archive'})

        # Nome da pasta onde o conteúdo será extraído
        extract_folder_name = os.path.splitext(os.path.basename(zip_filename))[0]
        extract_path = os.path.join(user_home, extract_folder_name)

        # Criar o diretório de extração se ele não existir
        if not os.path.exists(extract_path):
            os.makedirs(extract_path)

        # Extraindo o arquivo para a pasta de destino, evitando diretórios duplicados
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                # Extrair apenas o conteúdo sem criar um diretório raiz duplicado
                member_path = os.path.join(extract_path, os.path.basename(member))
                if not os.path.isdir(member_path):
                    with zip_ref.open(member) as source, open(member_path, 'wb') as target:
                        target.write(source.read())

        # Ajustar permissões - dentro do diretório do usuário logado
        subprocess.run(['sudo', 'chown', '-R', f'{request.user.username}:{request.user.username}', extract_path])
        subprocess.run(['sudo', 'chmod', '-R', '755', extract_path])

        # Criar um link simbólico no diretório /var/www/members/
        link_path = f"/var/www/members/{extract_folder_name}"
        if not os.path.exists(link_path):
            subprocess.run(['sudo', 'ln', '-s', extract_path, link_path])

        # Ajustar as permissões e proprietário no diretório /var/www/
        subprocess.run(['sudo', 'chown', '-R', 'www-data:www-data', '/var/www/'])
        subprocess.run(['sudo', 'chown', '-R', 'www-data:www-data', '/var/www/members/'])

        return JsonResponse({'status': 'success'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})



import os
import subprocess
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required
@csrf_exempt
def delete_file(request):
    if request.method == 'POST':
        try:
            # Carregar o JSON do corpo da requisição
            data = json.loads(request.body)
            paths = data.get('path') or data.get('paths')

            if not paths:
                return JsonResponse({'status': 'error', 'message': 'Nenhum arquivo especificado'})

            # Verificar se paths é uma lista (múltiplos arquivos) ou uma string (um único arquivo)
            if isinstance(paths, str):
                paths = [paths]  # Transformar em lista para processamento uniforme

            # Caminho completo dos arquivos na pasta home do usuário
            user_home = os.path.expanduser(f"~{request.user.username}")
            for filename in paths:
                file_path = os.path.join(user_home, filename)

                # Verificar se o arquivo existe
                if not os.path.exists(file_path):
                    return JsonResponse({'status': 'error', 'message': f'Arquivo não encontrado: {filename}'})

                # Remover o arquivo com sudo
                subprocess.run(['sudo', 'rm', '-f', file_path], check=True)

            return JsonResponse({'status': 'success'})

        except subprocess.CalledProcessError as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'failed', 'message': 'Método de requisição inválido'})
