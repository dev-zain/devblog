from django.shortcuts import render, redirect, get_object_or_404
from django.contrib. auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from . forms import SignUpForm, LoginForm, ProfileUpdateForm, UserUpdateForm
from . models import Profile


def register_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('blog:post_list')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
        
            # Log the user in
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('blog:post_list')
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/register.html', {'form': form})


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
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                # Redirect to 'next' parameter or homepage
                next_url = request.GET.get('next', 'blog:post_list')
                return redirect(next_url)
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