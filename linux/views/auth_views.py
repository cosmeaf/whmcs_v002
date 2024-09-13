from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from linux.forms import UserLoginForm, UserRegisterForm, UserRecoveryForm, OtpVerifyForm, PasswordResetConfirmForm
from django.views.generic import TemplateView


def logout_view(request):
    logout(request)
    return redirect('login')

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = UserLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard')


class UserRegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()
        login(self.request, user)

        return super().form_valid(form)



class UserRecoveryView(FormView):
    template_name = 'accounts/recovery.html'
    form_class = UserRecoveryForm
    success_url = reverse_lazy('otp_validation')
    error_url = reverse_lazy('recovery_done')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        user = User.objects.get(email=email)
        form.send_recovery_email()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)



class OtpValidationView(FormView):
    template_name = 'accounts/otp_validation.html'
    form_class = OtpVerifyForm
    success_url = reverse_lazy('success')
    error_url = reverse_lazy('otp_validation')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)



class SuccessView(TemplateView):
    template_name = 'accounts/success.html'


class PasswordResetConfirmView(FormView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = PasswordResetConfirmForm
    success_url = reverse_lazy('password_reset_complete')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['token'] = self.kwargs.get('token')
        kwargs['uidb64'] = self.kwargs.get('uidb64')
        return kwargs

    def form_valid(self, form):
        if not form.user:
            return redirect('password_reset_error')
        return super().form_valid(form)


class PasswordResetCompleteView(TemplateView):
    template_name = 'accounts/password_reset_complete.html'


class UserDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['username'] = user.username
        context['email'] = user.email
        return context

