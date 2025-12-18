from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile  

class SignUpForm(UserCreationForm):
    """Custom registration form with email"""
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder':  'Email'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':  'Username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs. update({
            'class': 'form-control',
            'placeholder':  'Password'
        })
        self.fields['password2']. widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })


class LoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling"""
    username = forms. CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder':  'Password'
        })
    )


class ProfileUpdateForm(forms.ModelForm):
    """Form to update user profile"""
    class Meta:
        model = Profile  # ← This now correctly references accounts. models.Profile
        fields = ['avatar', 'bio', 'location', 'website']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself.. .'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':  'City, Country'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }


class UserUpdateForm(forms.ModelForm):
    """Form to update user information"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }