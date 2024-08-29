import os
import subprocess
from django.db.models.signals import post_save, pre_save, post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from linux.utilities.create_user import create_linux_user
from linux.utilities.delete_user import delete_linux_user
from linux.utilities.update_user import update_password
from .models import Subdomain

@receiver(post_save, sender=User)
def create_user_signal(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        create_linux_user(instance.username, instance.password)

@receiver(post_delete, sender=User)
def delete_user_signal(sender, instance, **kwargs):
    delete_linux_user(instance.username)

@receiver(pre_save, sender=User)
def update_password_signal(sender, instance, **kwargs):
    if instance.pk:
        user = User.objects.get(pk=instance.pk)
        if user.password != instance.password:
            update_password(instance.username, instance.password)


@receiver(post_save, sender=Subdomain)
def create_project_directory_and_symlinks(sender, instance, created, **kwargs):
    user_home = f"/home/{instance.user.username}"
    project_dir = os.path.join(user_home, instance.name)
    link_dir = f"/var/www/members/{instance.name}"

    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
        os.chown(project_dir, instance.user.id, instance.user.id)  # Define o proprietário correto para o diretório
        print(f"Diretório do projeto criado: {project_dir}")

    if not os.path.exists(link_dir):
        os.makedirs(link_dir)

    for dir_name in os.listdir(user_home):
        full_dir_path = os.path.join(user_home, dir_name)
        if os.path.isdir(full_dir_path):
            link_path = os.path.join(link_dir, dir_name)
            if not os.path.exists(link_path):
                os.symlink(full_dir_path, link_path)
                print(f"Link simbólico criado para {dir_name} em {link_path}")

    # Configura as permissões para o diretório do usuário e o projeto
    subprocess.run(['sudo', 'chmod', '755', user_home])
    subprocess.run(['sudo', 'chmod', '-R', '755', project_dir])
    subprocess.run(['sudo', 'chown', '-R', 'www-data:www-data', project_dir])
    subprocess.run(['sudo', 'chown', '-R', 'www-data:www-data', '/var/www/'])
    subprocess.run(['sudo', 'chown', '-R', 'www-data:www-data', '/var/www/members/'])
    print(f"Permissões ajustadas para o diretório do usuário e o projeto: {project_dir}")


@receiver(post_save, sender=User)
def adjust_permissions_and_links(sender, instance, created, **kwargs):
    if created:
        user_home = os.path.expanduser(f"~{instance.username}")
        extracted_folders = [f for f in os.listdir(user_home) if os.path.isdir(os.path.join(user_home, f))]

        for folder in extracted_folders:
            folder_path = os.path.join(user_home, folder)
            os.system(f"chown -R {instance.username}:{instance.username} {folder_path}")
            os.system(f"ln -s {folder_path} /var/www/members/{folder}")
            os.system(f"chown -R www-data:www-data /var/www/members/{folder}")