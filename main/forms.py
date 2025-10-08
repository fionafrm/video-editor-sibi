from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'contoh@email.com'
        }),
        help_text="Email akan digunakan untuk reset password"
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize widget attributes and help texts
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Pilih username unik'
        })
        self.fields['username'].help_text = "Maksimal 150 karakter. Hanya huruf, angka, dan @/./+/-/_ yang diperbolehkan."
        
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Buat password yang kuat'
        })
        self.fields['password1'].help_text = ""
        
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ketik ulang password'
        })
        self.fields['password2'].help_text = ""
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email sudah terdaftar. Silakan gunakan email lain.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan email terdaftar Anda'
        }),
        help_text="Kami akan mengirimkan link reset password ke email ini"
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError("Email tidak ditemukan dalam sistem kami.")
        return email


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan password baru'
        }),
        help_text="Password harus minimal 8 karakter"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Konfirmasi password baru'
        }),
        help_text="Ketik ulang password yang sama"
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password saat ini'
        }),
        help_text="Masukkan password lama Anda"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password baru'
        }),
        help_text="Minimal 8 karakter"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Konfirmasi password baru'
        }),
        help_text="Ketik ulang password baru"
    )