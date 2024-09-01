import subprocess
import logging

logger = logging.getLogger('linux_manager')

def update_password(username, new_password):
    """Atualiza a senha do usuário no sistema Linux."""
    try:
        # Gera a senha criptografada usando openssl
        encrypted_password = subprocess.run(
            ['openssl', 'passwd', '-1', new_password],
            capture_output=True, text=True, check=True
        ).stdout.strip()

        # Atualiza a senha do usuário no Linux
        subprocess.run(['sudo', 'usermod', '-p', encrypted_password, username], check=True)
        logger.info(f'Senha do usuário {username} atualizada com sucesso no Linux')

    except subprocess.CalledProcessError as e:
        logger.error(f'Erro ao atualizar a senha do usuário {username} no Linux: {e}')
    except FileNotFoundError as e:
        logger.error(f'Erro ao executar o comando: arquivo ou diretório não encontrado: {e}')
    except Exception as e:
        logger.error(f'Ocorreu um erro inesperado ao atualizar a senha do usuário {username}: {e}')


def update_username(old_username, new_username):
    """Atualiza o nome de usuário no sistema Linux."""
    try:
        # Atualiza o nome de usuário no Linux
        subprocess.run(['sudo', 'usermod', '-l', new_username, old_username], check=True)

        # Opcionalmente, atualize o diretório home também, se necessário
        subprocess.run(['sudo', 'usermod', '-d', f'/home/{new_username}', '-m', new_username], check=True)

        logger.info(f'Nome de usuário atualizado de {old_username} para {new_username} no Linux com sucesso')

    except subprocess.CalledProcessError as e:
        logger.error(f'Erro ao atualizar o nome de usuário de {old_username} para {new_username} no Linux: {e}')
    except FileNotFoundError as e:
        logger.error(f'Erro ao executar o comando: arquivo ou diretório não encontrado: {e}')
    except Exception as e:
        logger.error(f'Ocorreu um erro inesperado ao atualizar o nome de usuário de {old_username} para {new_username}: {e}')
