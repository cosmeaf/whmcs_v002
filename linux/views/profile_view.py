# linux/views/profile_view.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages
from linux.models import UserProfile
from linux.forms import UserProfileForm

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/profile.html'

class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'dashboard/change_password.html'
    success_url = reverse_lazy('profile')


@login_required
def edit_profile(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('profile') 
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'dashboard/edit_profile.html', {'form': form})
