from django.urls import path
from django.views.generic.base import TemplateView
from .views.home_view import home_view
from .views.dashboard_views import dashboard
from .views.projects_views import projects, project_detail, upload_to_home, save_file_content, unzip_file, delete_file
from linux.views.profile_view import ProfileView, ChangePasswordView, edit_profile
from linux.views import auth_views


urlpatterns = [
    path('', home_view, name='home'),
    path('login/', auth_views.UserLoginView.as_view(), name='login'),
    path('register/', auth_views.UserRegisterView.as_view(), name='register'),
    path('recovery/', auth_views.UserRecoveryView.as_view(), name='recovery'),
    path('recovery/done/', TemplateView.as_view(template_name='accounts/recovery_done.html'), name='recovery_done'),
    path('otp/validate/', auth_views.OtpValidationView.as_view(), name='otp_validation'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password_reset_error/', TemplateView.as_view(template_name='accounts/password_reset_error.html'), name='password_reset_error'),
    path('success/', auth_views.SuccessView.as_view(), name='success'),
    path('logout/', auth_views.logout_view, name='logout'),


    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/projects/', projects, name='projects'),
    path('dashboard/projects/<path:name_project>/', project_detail, name='project_detail'),
    path('dashboard/upload_to_home/', upload_to_home, name='upload_to_home'),
    path('dashboard/save_file_content/', save_file_content, name='save_file_content'),
    path('dashboard/unzip_file/', unzip_file, name='unzip_file'),
    path('dashboard/delete_file/', delete_file, name='delete_file'),
    path('dashboard/profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('dashboard/change_password/', ChangePasswordView.as_view(), name='change_password'),
]
