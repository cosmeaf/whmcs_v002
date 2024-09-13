import random
from django import forms
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from linux.tasks import send_email_task
from django.core.exceptions import ValidationError
from django.utils.encoding import force_bytes 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm
from .models import OtpCode, UserProfile



class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Username'
        }),
        label='Username',
        min_length=7,
        error_messages={
            'required': 'This field is required.',
            'min_length': 'Username must be at least 7 characters long.'
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-sm', 
            'placeholder': 'Password'
        }),
        label='Password',
        error_messages={
            'required': 'This field is required.'
        }
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('Username or password invalid.')

        return cleaned_data



class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'First Name'
        }),
        label='First Name',
        max_length=30,
        error_messages={
            'required': 'This field is required.',
        }
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Last Name'
        }),
        label='Last Name',
        max_length=30,
        error_messages={
            'required': 'This field is required.',
        }
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Username'
        }),
        label='Username',
        max_length=150,
        error_messages={
            'required': 'This field is required.',
        }
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Email'
        }),
        label='Email',
        error_messages={
            'required': 'This field is required.',
            'invalid': 'Enter a valid email address.',
        }
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def save(self, commit=True):
        # Salva o usuário sem confirmar a senha
        user = super(UserRegisterForm, self).save(commit=False)
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        
        # Define a senha com o método apropriado
        user.set_password(self.cleaned_data.get('password1'))
        
        if commit:
            user.save()
        
        return user



class UserRecoveryForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Enter your email'
        }),
        label='Email',
        error_messages={
            'required': 'This field is required.',
            'invalid': 'Enter a valid email address.'
        }
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError('Email not registered or not found.')
        return email

    def send_recovery_email(self):
        email = self.cleaned_data.get('email')
        user = User.objects.get(email=email)
        otp_code = str(random.randint(100000, 999999))
        OtpCode.objects.update_or_create(user=user, defaults={'code': otp_code, 'created_at': timezone.now()})
        send_email_task.delay(
        subject='Password Recovery',
        to_email=email,
        body=f'Your OTP code for password recovery is: {otp_code}'
        )



class OtpVerifyForm(forms.Form):
    otp_code = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Enter OTP code'
        }),
        label='OTP Code',
        max_length=6,
        error_messages={
            'required': 'This field is required.',
        }
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_otp_code(self):
        otp_code = self.cleaned_data.get('otp_code')
        try:
            otp_entry = OtpCode.objects.get(code=otp_code)
            now = timezone.now()
            expiration_time = otp_entry.created_at + timedelta(minutes=15)
            if now > expiration_time:
                raise ValidationError('OTP code has expired.')

            # Gerar um token para redefinição de senha
            user = otp_entry.user
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(self.request).domain
            reset_link = f'http://{domain}/reset/{uid}/{token}/'

            # Enviar o link de redefinição por e-mail
            send_email_task.delay(
            subject='Password Reset',
            to_email=user.email,
            body=f'Click the link below to reset your password:\n{reset_link}'
            )


            return otp_code
        except OtpCode.DoesNotExist:
            raise ValidationError('Invalid OTP code.')



class PasswordResetConfirmForm(SetPasswordForm):
    """
    A form for resetting the password with additional functionality for token and uidb64.
    """
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'New Password'
        }),
        label='New Password',
        error_messages={
            'required': 'This field is required.'
        }
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Confirm New Password'
        }),
        label='Confirm New Password',
        error_messages={
            'required': 'This field is required.'
        }
    )

    def __init__(self, *args, **kwargs):
        token = kwargs.pop('token', None)
        uidb64 = kwargs.pop('uidb64', None)
        self.user = self.get_user(uidb64, token)
        super().__init__(user=self.user, *args, **kwargs)

    def get_user(self, uidb64, token):
        """
        Retrieve the user based on the uidb64 and token.
        """
        UserModel = get_user_model()
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            return user
        return None

    def clean(self):
        cleaned_data = super().clean()
        if not self.user:
            raise forms.ValidationError("Invalid reset link.")
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image',  'location', 'birth_date', 'website', 'github', 'linkedin', 'twitter', 'bio']
