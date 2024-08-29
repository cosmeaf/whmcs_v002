from django.urls import path
from .views.auth_views import signup, user_login
from .views.dashboard_views import dashboard, user_logout
from .views.projects_views import projects, project_detail, upload_project, save_file_content, unzip_file, delete_file

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/projects/', projects, name='projects'),
    path('dashboard/projects/<str:name_project>/', project_detail, name='project_detail'),
    path('dashboard/upload_project/', upload_project, name='upload_project'),
    path('dashboard/save_file_content/', save_file_content, name='save_file_content'),
    path('dashboard/unzip_file/', unzip_file, name='unzip_file'),
    path('dashboard/delete_file/', delete_file, name='delete_file'),

]
