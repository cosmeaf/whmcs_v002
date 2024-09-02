from django.urls import path
from django.contrib.auth import views as auth_views
from .views.auth_views import user_login
from .views.dashboard_views import dashboard, user_logout
from .views.projects_views import projects, project_detail, upload_to_home, save_file_content, unzip_file, delete_file

urlpatterns = [
    path('', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/projects/', projects, name='projects'),
    path('dashboard/projects/<path:name_project>/', project_detail, name='project_detail'),
    path('dashboard/upload_to_home/', upload_to_home, name='upload_to_home'),
    path('dashboard/save_file_content/', save_file_content, name='save_file_content'),
    path('dashboard/unzip_file/', unzip_file, name='unzip_file'),
    path('dashboard/delete_file/', delete_file, name='delete_file'),
    
    # URLs para recuperação de senha usando as views padrão do Django
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
