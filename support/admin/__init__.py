from .smtp_admin import EmailSettingsAdmin
from django.contrib import admin
from support.models.user_manager_model import UserManager
from support.admin.user_manager_admin import UserManagerAdmin

admin.site.register(UserManager, UserManagerAdmin)

