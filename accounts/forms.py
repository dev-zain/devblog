from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile  

class SignUpForm(UserCreationForm):
    """Custom registration form with email, first name, and last name"""
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder':  'Email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':  'Username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder':  'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    
    def clean_username(self):
        """Convert username to lowercase"""
        username = self.cleaned_data.get('username')
        if username:
            username = username.lower()
            # Check if lowercase username already exists
            if User.objects.filter(username__iexact=username).exists():
                raise forms.ValidationError("A user with that username already exists.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    
    def save(self, commit=True):
        """Save user with lowercase username"""
        user = super().save(commit=False)
        user.username = user.username.lower()
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling"""
    username = forms.CharField(
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
    
    def clean_username(self):
        """Convert username to lowercase for login"""
        username = self.cleaned_data.get('username')
        if username:
            username = username.lower()
        return username


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
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }
    
    def clean_username(self):
        """Convert username to lowercase"""
        username = self.cleaned_data.get('username')
        if username:
            username = username.lower()
            # Check if lowercase username already exists (excluding current user)
            existing_user = User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise forms.ValidationError("A user with that username already exists.")
        return username
    
    def save(self, commit=True):
        """Save user with lowercase username"""
        user = super().save(commit=False)
        user.username = user.username.lower()
        if commit:
            user.save()
        return user