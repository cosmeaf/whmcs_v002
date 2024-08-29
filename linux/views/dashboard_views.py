from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('login')

@login_required
def dashboard(request):
    return render(request, 'dashboard/index.html')