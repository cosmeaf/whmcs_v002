import os
from django.db import models
from django.contrib.auth.models import User

class Subdomain(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_symbolic_links()

    def create_symbolic_links(self):
        user_home = f"/home/{self.user.username}"
        link_dir = f"/var/www/members/{self.name}"

        if not os.path.exists(link_dir):
            os.makedirs(link_dir)

        for dir_name in os.listdir(user_home):
            full_dir_path = os.path.join(user_home, dir_name)
            if os.path.isdir(full_dir_path):
                link_path = os.path.join(link_dir, dir_name)
                if not os.path.exists(link_path):
                    os.symlink(full_dir_path, link_path)
                    print(f"Link simbólico criado para {dir_name} em {link_path}")

    def __str__(self):
        return f"{self.name}"
