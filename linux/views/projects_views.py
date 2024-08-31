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
        file_path = os.path.join(user_home, upload_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in upload_file.chunks():
                destination.write(chunk)
        uid = pwd.getpwnam(request.user.username).pw_uid
        gid = grp.getgrnam(request.user.username).gr_gid
        os.chown(file_path, uid, gid)
        os.chmod(file_path, 0o644)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed', 'message': 'No file uploaded'})


@login_required
@csrf_exempt
def save_file_content(request):
    if request.method == 'POST':
        try:
            file_path = os.path.join(os.path.expanduser(f"~{request.user.username}"), request.POST.get('path'))
            content = request.POST.get('content')
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


@login_required
@require_POST
def delete_file(request):
    # Define o caminho base fixo para o diretório home do usuário logado
    user_home = f"/home/{request.user.username}"
    logger.info(f"Log 1: Caminho base do usuário: {user_home}")
    
    # Obtém os caminhos dos arquivos enviados via POST no corpo da requisição JSON
    try:
        data = json.loads(request.body)
        paths = data.get('paths', [])
    except json.JSONDecodeError:
        logger.error("Erro ao decodificar JSON recebido.")
        return JsonResponse({'success': False, 'message': 'Erro ao processar a solicitação. JSON inválido.'})

    logger.info(f"Log 2: Arquivos recebidos via POST: {paths}")
    errors = []
    logger.info(f"Usuário {request.user.username} iniciou o processo de exclusão.")
    
    for path in paths:
        # Constrói o caminho completo do arquivo/diretório com base no nome recebido
        full_path = os.path.join(user_home, path.lstrip('/'))
        logger.info(f"Log 3: Processando o caminho para exclusão: {full_path}")      
        if os.path.basename(full_path).startswith('.'):
            logger.info(f"Ignorando {full_path}: Arquivo ou diretório oculto ou essencial.")
            errors.append(f"Ignorado: {path} (Arquivo oculto ou essencial)")
            continue      
        if os.path.exists(full_path):
            logger.info(f"Log 4: {full_path} existe e será processado para exclusão.")
            try:
                if os.path.isdir(full_path):
                    logger.info(f"Log 5: {full_path} é um diretório.")
                    # Caminho do link simbólico relacionado ao diretório
                    link_path = f"/var/www/members/{os.path.basename(full_path)}"
                    if os.path.islink(link_path):
                        logger.info(f"Log 6: Removendo link simbólico {link_path}.")
                        os.unlink(link_path)                  
                    logger.info(f"Log 7: Tentando remover o diretório {full_path}.")
                    result = subprocess.run(['sudo', 'rm', '-rf', full_path], check=True)
                    logger.info(f"Log 8: Remoção do diretório {full_path} concluída com status: {result.returncode}")              
                elif os.path.isfile(full_path) or os.path.islink(full_path):
                    logger.info(f"Log 5: {full_path} é um arquivo ou link simbólico.")
                    logger.info(f"Log 7: Tentando remover o arquivo/link {full_path}.")
                    result = subprocess.run(['sudo', 'rm', '-f', full_path], check=True)
                    logger.info(f"Log 8: Remoção do arquivo/link {full_path} concluída com status: {result.returncode}")          
            except Exception as e:
                logger.error(f"Erro ao excluir {full_path}: {str(e)}")
                errors.append(f"Erro ao excluir {path}: {str(e)}")
        else:
            logger.info(f"Log 4: {full_path} não encontrado.")
            errors.append(f"{path} não encontrado.")   
    if errors:
        logger.info(f"Processo de exclusão concluído com erros: {' '.join(errors)}")
        return JsonResponse({'success': False, 'message': ' '.join(errors)})
    else:
        logger.info("Processo de exclusão concluído com sucesso.")
        return JsonResponse({'success': True})
