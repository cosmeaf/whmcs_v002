import subprocess
import logging

logger = logging.getLogger('linux_manager')

def update_password(username, new_password):
    """Atualiza a senha do usuário no sistema Linux."""
    try:
        encrypted_password = subprocess.run(
            ['openssl', 'passwd', '-1', new_password],
            capture_output=True, text=True
        ).stdout.strip()

        subprocess.run(['sudo', 'usermod', '-p', encrypted_password, username], check=True)
        logger.info(f'Senha do usuário {username} atualizada com sucesso no Linux')
    except subprocess.CalledProcessError as e:
        logger.error(f'Erro ao atualizar a senha do usuário {username} no Linux: {e}')
