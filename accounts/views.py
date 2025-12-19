from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode  # ← NEW
from django.utils.encoding import force_str  # ← NEW
from . forms import SignUpForm, LoginForm, ProfileUpdateForm, UserUpdateForm
from . models import Profile
from . tokens import account_activation_token  # ← NEW
from . utils import send_activation_email  # ← NEW


def register_view(request):
    """Handle user registration with email verification"""
    if request.user.is_authenticated:
        return redirect('blog:post_list')
    
    if request.method == 'POST': 
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Create user but set as inactive  ← CHANGED
            user = form.save(commit=False)  # ← CHANGED
            user.is_active = False  # ← NEW:  User can't login until email verified
            user.save()  # ← CHANGED
            
            # Send activation email  ← NEW
            send_activation_email(request, user)  # ← NEW
            
            # Show confirmation page  ← NEW
            return render(request, 'accounts/activation_sent.html', {  # ← CHANGED
                'email': user.email  # ← NEW
            })  # ← CHANGED
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def activate(request, uidb64, token):  # ← COMPLETELY NEW FUNCTION
    """Activate user account via email link"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        # Activate user
        user.is_active = True
        user.save()
        
        # Mark email as verified
        user.profile.email_verified = True
        user.profile.save()
        
        messages.success(request, 'Your account has been activated! You can now log in.')
        return render(request, 'accounts/activation_complete.html')
    else:
        return render(request, 'accounts/activation_invalid.html')


def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('blog:post_list')
    
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if user is active (email verified)  ← NEW
                if user.is_active:  # ← NEW
                    login(request, user)
                    messages.success(request, f'Welcome back, {username}!')
                    # Redirect to 'next' parameter or homepage
                    next_url = request.GET.get('next', 'blog:post_list')
                    return redirect(next_url)
                else:  # ← NEW BLOCK
                    messages.error(request, 'Please activate your account first.  Check your email.')  # ← NEW
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('blog:post_list')


def profile_view(request, username):
    """Display user profile (public view)"""
    user = get_object_or_404(User, username=username)
    profile = user.profile
    posts = user.post_set.filter(status='published').order_by('-created_at')[: 5]
    
    context = {
        'profile_user': user,
        'profile': profile,
        'posts':  posts,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    """Edit logged-in user's profile"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES,  # For avatar upload
            instance=request.user.profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile', username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile_edit.html', context)