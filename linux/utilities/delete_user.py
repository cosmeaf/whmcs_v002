import subprocess
import logging

logger = logging.getLogger('linux_manager')

def delete_linux_user(username):
    try:
        subprocess.run(['sudo', 'userdel', '-rf', username], check=True)
        logger.info(f'Usuário Linux {username} excluído com sucesso')
    except subprocess.CalledProcessError as e:
        logger.error(f'Erro ao excluir o usuário Linux {username}: {e}')
