import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from linux.models import ProjectAccess
import logging

# Configure logging
logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    # Diretório base do usuário
    user_home = f"/home/{request.user.username}"
    
    # Contagem de projetos (pastas)
    projects = []
    total_usage = 0
    if os.path.exists(user_home):
        for item in os.listdir(user_home):
            item_path = os.path.join(user_home, item)
            if os.path.isdir(item_path):  # Contar somente diretórios
                projects.append(item)
                # Calcular uso total de espaço em disco
                for dirpath, dirnames, filenames in os.walk(item_path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        total_usage += os.path.getsize(fp)

    total_projects = len(projects)

    # Convertendo total_usage de bytes para megabytes
    total_usage_mb = total_usage / (1024 * 1024)
    limit_mb = 500

    # Determinar cor do status baseado no uso
    if total_usage_mb < (limit_mb * 0.5):
        usage_status = 'bg-success'  # Verde para uso baixo
    elif total_usage_mb < (limit_mb * 0.8):
        usage_status = 'bg-warning'  # Amarelo para uso moderado
    else:
        usage_status = 'bg-danger'  # Vermelho para uso alto

    # Construção das URLs dinâmicas com base na URL do sistema
    base_url = request.get_host()  # Obtém o host atual
    scheme = request.scheme  # Obtém o esquema (http ou https)
    project_urls = [f"{scheme}://{project}.{base_url}" for project in projects]

    # Contagem de acessos
    total_access = ProjectAccess.objects.filter(user=request.user).count()
    logger.info(f"Total de acessos. = {total_access}")

    # Passar os dados para o template
    context = {
        'total_projects': total_projects,
        'total_usage': total_usage_mb,
        'total_access': total_access,
        'usage_status': usage_status,
        'project_urls': project_urls,
    }

    return render(request, 'dashboard/index.html', context)
