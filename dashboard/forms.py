from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile

class UserEditForm(forms.ModelForm):
    """Form for editing basic user information"""
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Masukkan nama depan'
        }),
        label='Nama Depan'
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Masukkan nama belakang'
        }),
        label='Nama Belakang'
    )
    
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'contoh@email.com'
        }),
        label='Email'
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email is already taken by another user
            existing_user = User.objects.filter(email=email).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise ValidationError("Email sudah digunakan oleh pengguna lain.")
        return email

class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information"""
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Ceritakan sedikit tentang diri Anda...',
            'rows': 4,
            'maxlength': 500
        }),
        label='Bio',
        help_text='Maksimal 500 karakter'
    )
    
    class Meta:
        model = UserProfile
        fields = ['bio']