import subprocess
import logging

logger = logging.getLogger('linux_manager')

def create_linux_user(username, password):
    try:
        logger.info(f'Iniciando criação do usuário Linux: {username}')        
        encrypted_password = subprocess.run(
            ['openssl', 'passwd', '-1', password],
            capture_output=True, text=True
        ).stdout.strip()

        subprocess.run([
            'sudo', 'useradd', '-m',
            '-p', encrypted_password,
            '-c', 'User Web Cpanel',
            '-s', '/bin/bash',
            username
        ], check=True)

        subprocess.run(['sudo', 'chmod', '700', f'/home/{username}'], check=True)
        subprocess.run(['sudo', 'chmod', '-R', 'g+rwx', '/var/www'], check=True)
        subprocess.run(['sudo', 'usermod', '-aG', 'www-data', username], check=True)
        subprocess.run(['sudo', 'chown', '-R', 'www-data:www-data', '/var/www'], check=True)
        subprocess.run(['sudo', 'chmod', 'g+s', '/var/www'], check=True)
        logger.info(f'Usuário Linux {username} criado com sucesso')

    except subprocess.CalledProcessError as e:
        logger.error(f'Erro ao criar e configurar o usuário Linux: {e}')
