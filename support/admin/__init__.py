# from .smtp_admin import EmailSettingsAdmin
from .smtp_task_admin import EmailSettingsAdmin
from django.contrib import admin
from django.contrib.auth.models import User
from support.models.user_manager_model import UserManager
from support.admin.user_manager_admin import UserManagerAdmin
from support.admin.user_report_admin import CustomUserReport

# Desregistrar o UserAdmin padrão
admin.site.unregister(User)

# Registrar o User com a nova classe de admin
admin.site.register(User, CustomUserReport)

# Registro do modelo UserManager com a classe UserManagerAdmin
admin.site.register(UserManager, UserManagerAdmin)

