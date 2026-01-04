from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode  # ← NEW
from django.utils.encoding import force_str  # ← NEW
from django.core.paginator import Paginator
from blog.models import Post
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
            try:
                # Create user as INACTIVE (requires email verification)
                user = form.save(commit=False)
                user.is_active = False  # ✅ User must verify email first
                user.save()
                
                # Try to send activation email
                try: 
                    send_activation_email(request, user)
                    messages.info(
                        request, 
                        f'Account created for {user.username}! '
                        f'Please check your email inbox or spam folder ({user.email}) to activate your account.'
                    )
                except Exception as e: 
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Email failed:  {e}")
                    messages.warning(
                        request, 
                        'Account created but we couldn\'t send the activation email.  '
                        'Please contact support.'
                    )
                
                # DO NOT login the user - they must verify email first
                # Redirect to login page with message
                return redirect('accounts:login')
                
            except Exception as e: 
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Registration error: {e}")
                import traceback
                logger.error(traceback.format_exc())
                messages.error(request, 'An error occurred during registration. Please try again.')
                
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/register.html', {'form':  form})


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
            username = form.cleaned_data.get('username')  # Already lowercase from form
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if user is active (email verified)
                if user.is_active:
                    login(request, user)
                    # Display full name if available, otherwise username
                    display_name = user.get_full_name() or user.username
                    messages.success(request, f'Welcome back, {display_name}!')
                    # Redirect to 'next' parameter or homepage
                    next_url = request.GET.get('next', 'blog:post_list')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Please activate your account first. Check your email.')
            else:
                messages.error(request, 'Invalid username or password.')
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
    # Show only 6 recent posts on profile page
    posts = user.post_set.filter(status='published').select_related('author', 'category').prefetch_related('tags').order_by('-created_at')[:6]
    total_posts_count = user.post_set.filter(status='published').count()
    
    context = {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
        'total_posts_count': total_posts_count,
    }
    return render(request, 'accounts/profile.html', context)


def user_posts_view(request, username):
    """Display all posts by a specific user with pagination"""
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(
        author=user,
        status='published'
    ).select_related('author', 'category').prefetch_related('tags').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile_user': user,
        'page_obj': page_obj,
        'posts': page_obj,
    }
    return render(request, 'accounts/user_posts.html', context)


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