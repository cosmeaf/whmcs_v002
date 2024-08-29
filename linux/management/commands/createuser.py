from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management import CommandError
from django.contrib.auth.password_validation import validate_password
from getpass import getpass

class Command(BaseCommand):
    help = 'Cria um usuário staff com o username, email, primeiro nome, e último nome fornecidos'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='Nome de usuário (obrigatório)')
        parser.add_argument('--email', type=str, help='Email do usuário (opcional)')
        parser.add_argument('--first_name', type=str, help='Primeiro nome do usuário (opcional)')
        parser.add_argument('--last_name', type=str, help='Último nome do usuário (opcional)')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        email = kwargs.get('email')
        first_name = kwargs.get('first_name')
        last_name = kwargs.get('last_name')

        if User.objects.filter(username=username).exists():
            raise CommandError(f"Usuário '{username}' já existe")

        password = None
        password_confirm = None

        while password is None:
            password = getpass('Senha: ')
            password_confirm = getpass('Confirme a senha: ')

            if password != password_confirm:
                self.stdout.write(self.style.ERROR("As senhas não coincidem. Tente novamente."))
                password = None
                continue

            try:
                validate_password(password)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro de validação da senha: {e}"))
                password = None

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = True

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name

        user.save()

        self.stdout.write(self.style.SUCCESS(f"Usuário staff '{username}' criado com sucesso"))
