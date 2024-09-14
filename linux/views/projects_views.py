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
    # Diretório home do usuário logado
    user_home = os.path.expanduser(f"~{request.user.username}")
    project_path = os.path.join(user_home, name_project)
    
    # Verifica se o caminho do projeto existe
    if not os.path.exists(project_path):
        return HttpResponse("Projeto não encontrado", status=404)

    # Lista os arquivos e pastas dentro do projeto
    files_and_folders = []
    for item in os.listdir(project_path):
        item_path = os.path.join(project_path, item)
        stats = os.stat(item_path)
        permissions = oct(stats.st_mode)[-3:]
        permission_str = f"{permissions} {pwd.getpwuid(stats.st_uid).pw_name} {grp.getgrgid(stats.st_gid).gr_name}"

        files_and_folders.append({
            'name': item,
            'type': 'Folder' if os.path.isdir(item_path) else 'File',
            'size': stats.st_size if os.path.isfile(item_path) else '-',
            'permissions': permission_str,
            'path': os.path.relpath(item_path, user_home),
            'is_file': os.path.isfile(item_path)
        })

    # Prepara o contexto para renderizar a página
    context = {
        'files_and_folders': files_and_folders,
        'current_project': name_project,
    }
    return render(request, 'dashboard/project_detail.html', context)


@login_required
@csrf_exempt
@require_POST
def upload_to_home(request):
    if request.method == 'POST' and request.FILES.get('file'):
        user_home = os.path.expanduser(f"~{request.user.username}")
        upload_file = request.FILES['file']

        # Salvar o arquivo no diretório /home/username/
        if not os.path.exists(user_home):
            os.makedirs(user_home)

        file_path = os.path.join(user_home, upload_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in upload_file.chunks():
                destination.write(chunk)

        # Ajustar permissões para o arquivo
        uid = pwd.getpwnam(request.user.username).pw_uid
        gid = grp.getgrnam(request.user.username).gr_gid
        os.chown(file_path, uid, gid)
        os.chmod(file_path, 0o644)

        return JsonResponse({'status': 'success', 'message': 'Arquivo carregado e permissões ajustadas com sucesso!'})
    
    return JsonResponse({'status': 'failed', 'message': 'Nenhum arquivo foi enviado.'})


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
        data = json.loads(request.body)
        zip_filename = data.get('path')

        if not zip_filename:
            return JsonResponse({'status': 'error', 'message': 'Invalid file path'})

        # Diretório home do usuário logado
        user_home = f"/home/{request.user.username}"
        zip_path = os.path.join(user_home, zip_filename)

        if not os.path.exists(zip_path):
            return JsonResponse({'status': 'error', 'message': 'File not found'})

        if not zipfile.is_zipfile(zip_path):
            return JsonResponse({'status': 'error', 'message': 'The file is not a valid .zip archive'})

        # Nome da pasta onde o conteúdo será extraído
        extract_folder_name = os.path.splitext(os.path.basename(zip_filename))[0]
        extract_path = os.path.join(user_home, extract_folder_name)

        # Se a pasta já existir, vamos removê-la para evitar duplicados
        if os.path.exists(extract_path):
            subprocess.run(['rm', '-rf', extract_path])

        # Criar o diretório de extração
        os.makedirs(extract_path)

        # Extraindo o arquivo diretamente para a pasta de destino
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                member_path = os.path.join(extract_path, os.path.basename(member))
                if not os.path.isdir(member_path):
                    with zip_ref.open(member) as source, open(member_path, 'wb') as target:
                        target.write(source.read())

        # Ajustar permissões - dentro do diretório do usuário logado
        subprocess.run(['chmod', '755', f'/home/{request.user.username}'])
        subprocess.run(['chmod', '755', extract_path])
        subprocess.run(['chmod', '-R', '644', f'{extract_path}/*'])
        subprocess.run(['sudo', 'chown', '-R', f'{request.user.username}:{request.user.username}', extract_path])

        # Criar link simbólico em /var/www/members/
        link_path = f"/var/www/members/{extract_folder_name}"
        if not os.path.exists(link_path):
            subprocess.run(['ln', '-s', extract_path, link_path])

        # Ajustar permissões de /var/www/members/
        subprocess.run(['chown', '-R', 'www-data:www-data', '/var/www/members/'])

        return JsonResponse({'status': 'success'})

    except Exception as e:
        logger.error(f"Error unzipping file: {str(e)}")
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
                # Remover qualquer tipo de arquivo ou diretório
                logger.info(f"Log 5: Tentando remover {full_path}.")
                result = subprocess.run(['sudo', 'rm', '-rf', full_path], check=True)
                logger.info(f"Log 6: Remoção de {full_path} concluída com status: {result.returncode}")         
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
