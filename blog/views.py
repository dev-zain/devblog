from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
from . models import Post, Comment, Category, Tag, Like
from . forms import PostForm, CommentForm
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods


def post_list(request):
    """Display homepage with featured, latest, recent, and most liked posts"""
    
    # Featured posts (admin selected, published only)
    featured_posts_qs = Post.objects.filter(
        status='published',
        is_featured=True
    ).select_related('author').order_by('-created_at')[:5]
    
    # Check if we have explicitly featured posts
    has_explicit_featured = featured_posts_qs.exists()
    
    # Get featured post IDs to exclude them from other sections (only if explicitly featured)
    if has_explicit_featured:
        featured_posts_list = list(featured_posts_qs)
        featured_ids = [post.id for post in featured_posts_list]
    else:
        # If no explicit featured posts, show most liked as featured but don't exclude from other sections
        featured_posts_list = list(Post.objects.filter(
            status='published'
        ).select_related('author').order_by('-like_count', '-created_at')[:5])
        # Don't exclude from other sections if auto-selected
        featured_ids = []
    
    # Latest posts (most recent, published, excluding explicitly featured only)
    latest_posts_qs = Post.objects.filter(
        status='published'
    ).exclude(id__in=featured_ids).select_related('author').order_by('-created_at')
    latest_posts = latest_posts_qs[:6]
    latest_posts_count = latest_posts_qs.count()
    
    # Recently uploaded (posts from last 7 days, excluding explicitly featured only)
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_posts_qs = Post.objects.filter(
        status='published',
        created_at__gte=seven_days_ago
    ).exclude(id__in=featured_ids).select_related('author').order_by('-created_at')
    recent_posts = recent_posts_qs[:6]
    recent_posts_count = recent_posts_qs.count()
    
    # Most liked posts (order by like_count, excluding explicitly featured only)
    from django.db.models import Count

    most_liked_posts_qs = (
        Post.objects.filter(status='published')
        
        .select_related('author')
        .annotate(likes_total=Count('likes'))
        .filter(likes_total__gt=0)
        .order_by('-likes_total', '-created_at')
    )
    most_liked_posts = most_liked_posts_qs[:6]
    most_liked_posts_count = most_liked_posts_qs.count()
    
    # Stats for hero section
    total_posts = Post.objects.filter(status='published').count()
    total_authors = User.objects.filter(post__status='published').distinct().count()
    total_likes = Post.objects.filter(status='published').aggregate(Sum('like_count'))['like_count__sum'] or 0
    
    return render(request, 'blog/post_list.html', {
        'featured_posts': featured_posts_list,
        'has_explicit_featured': has_explicit_featured,
        'latest_posts': latest_posts,
        'latest_posts_count': latest_posts_count,
        'recent_posts': recent_posts,
        'recent_posts_count': recent_posts_count,
        'most_liked_posts': most_liked_posts,
        'most_liked_posts_count': most_liked_posts_count,
        'total_posts': total_posts,
        'total_authors': total_authors,
        'total_likes': total_likes,
    })


def post_detail(request, slug):
    """Display a single blog post"""
    post = get_object_or_404(Post, slug=slug)
    
    # Allow authors to view their own drafts
    if post.status == 'draft' and (not request.user.is_authenticated or post.author != request.user):
        from django.http import Http404
        raise Http404("Post not found")
    
    # Only show published posts to non-authors
    if post.status != 'published' and (not request.user.is_authenticated or post.author != request.user):
        from django.http import Http404
        raise Http404("Post not found")
    
    comments = post.comments.filter(parent__isnull=True).order_by('-created_at')
    
    # Check if user has liked this post
    user_liked = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(user=request.user, post=post).exists()
    
    # Get related posts (same category or tags) - only published
    related_posts = Post.objects.filter(
        status='published'
    ).exclude(id=post.id)
    
    # Prioritize same category, then same tags
    if post.category:
        related_posts = related_posts.filter(
            Q(category=post.category) | Q(tags__in=post.tags.all())
        ).distinct()[:6]
    else:
        related_posts = related_posts.filter(
            tags__in=post.tags.all()
        ).distinct()[:6]
    
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'user_liked': user_liked,
        'related_posts': related_posts
    })


@login_required
def post_create(request):
    """Create a new blog post"""
    if request.method == 'POST': 
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            # Ensure content is not empty (check cleaned_data, not post.content)
            content = form.cleaned_data.get('content', '').strip()
            if not content or content == '<p><br></p>' or content == '<p></p>':
                form.add_error('content', 'Post content cannot be empty.')
                messages.error(request, 'Post content cannot be empty.')
                return render(request, 'blog/post_form.html', {
                    'form': form,
                    'title': 'Create New Post'
                })
            
            post.save()
            
            # Handle tags from comma-separated input
            tags_input = form.cleaned_data.get('tags_input', '').strip()
            if tags_input:
                tag_names = [name.strip() for name in tags_input.split(',') if name.strip()]
                # Remove duplicates
                seen = set()
                unique_tags = []
                for tag in tag_names:
                    if tag.lower() not in seen:
                        seen.add(tag.lower())
                        unique_tags.append(tag)
                
                # Limit to 3 tags
                unique_tags = unique_tags[:3]
                
                # Create or get tags
                tag_objects = []
                for tag_name in unique_tags:
                    tag, created = Tag.objects.get_or_create(
                        slug=slugify(tag_name),
                        defaults={'name': tag_name}
                    )
                    tag_objects.append(tag)
                
                post.tags.set(tag_objects)
            
            messages.success(request, 'Post created successfully!')
            # Redirect based on status
            if post.status == 'published':
                return redirect('blog:post_detail', slug=post.slug)
            else:
                return redirect('blog:my_posts')
        else:
            # Form is invalid - show errors
            messages.error(request, 'Please correct the errors below.')
            # Print form errors for debugging
            print("FORM ERRORS:", form.errors)
            print("FORM NON_FIELD_ERRORS:", form.non_field_errors())
            for field, errors in form.errors.items():
                print(f"Field {field}: {errors}")
    else:
        form = PostForm()
    
    return render(request, 'blog/post_form.html', {
        'form': form,
        'title': 'Create New Post'
    })


@login_required
def post_edit(request, slug):
    """Edit an existing blog post"""
    post = get_object_or_404(Post, slug=slug)
    
    # Check if user is the author
    if post.author != request.user:
        messages.error(request, 'You can only edit your own posts!')
        return redirect('blog:post_detail', slug=post.slug)
    
    if request.method == 'POST': 
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            # Ensure content is not empty
            content = form.cleaned_data.get('content', '').strip()
            if not content or content == '<p><br></p>' or content == '<p></p>':
                form.add_error('content', 'Post content cannot be empty.')
                messages.error(request, 'Post content cannot be empty.')
                return render(request, 'blog/post_form.html', {
                    'form': form,
                    'title': 'Edit Post',
                    'post': post
                })
            
            form.save()
            
            # Handle tags from comma-separated input
            tags_input = form.cleaned_data.get('tags_input', '').strip()
            if tags_input:
                tag_names = [name.strip() for name in tags_input.split(',') if name.strip()]
                # Remove duplicates
                seen = set()
                unique_tags = []
                for tag in tag_names:
                    if tag.lower() not in seen:
                        seen.add(tag.lower())
                        unique_tags.append(tag)
                
                # Limit to 3 tags
                unique_tags = unique_tags[:3]
                
                # Create or get tags
                tag_objects = []
                for tag_name in unique_tags:
                    tag, created = Tag.objects.get_or_create(
                        slug=slugify(tag_name),
                        defaults={'name': tag_name}
                    )
                    tag_objects.append(tag)
                
                post.tags.set(tag_objects)
            else:
                # Clear tags if input is empty
                post.tags.clear()
            
            messages.success(request, 'Post updated successfully!')
            return redirect('blog:post_detail', slug=post.slug)
        else:
            # Form is invalid - show errors
            messages.error(request, 'Please correct the errors below.')
            print("FORM ERRORS:", form.errors)
            for field, errors in form.errors.items():
                print(f"Field {field}: {errors}")
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/post_form.html', {
        'form': form,
        'title': 'Edit Post',
        'post': post
    })


@login_required
def post_delete(request, slug):
    """Delete a blog post"""
    post = get_object_or_404(Post, slug=slug)
    
    # Check if user is the author
    if post.author != request.user:
        messages.error(request, 'You can only delete your own posts!')
        return redirect('blog:post_detail', slug=post.slug)
    
    if request.method == 'POST':
        post. delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('blog:my_posts')
    
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


@login_required
def my_posts(request):
    """View all posts by the logged-in user"""
    published_posts = Post.objects.filter(
        author=request.user,
        status='published'
    ).select_related('category').prefetch_related('tags').order_by('-created_at')
    
    draft_posts = Post.objects.filter(
        author=request.user,
        status='draft'
    ).select_related('category').prefetch_related('tags').order_by('-created_at')
    
    return render(request, 'blog/my_posts.html', {
        'published_posts': published_posts,
        'draft_posts': draft_posts
    })


def category_list(request):
    """Display all categories with preview of latest posts"""
    # Show ALL categories, not just those with published posts
    categories = Category.objects.all().order_by('name')
    
    # Get latest posts for each category
    category_data = []
    for category in categories:
        latest_posts = category.posts.filter(
            status='published'
        ).select_related('author').prefetch_related('tags')[:5]
        
        category_data.append({
            'category': category,
            'latest_posts': latest_posts
        })
    
    return render(request, 'blog/categories.html', {
        'category_data': category_data
    })


def category_detail(request, slug):
    """Display posts in a specific category"""
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(
        category=category,
        status='published'
    ).select_related('author', 'category').prefetch_related('tags').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/category_detail.html', {
        'category': category,
        'page_obj': page_obj,
        'posts': page_obj
    })


def tag_detail(request, slug):
    """Display posts with a specific tag"""
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(
        tags=tag,
        status='published'
    ).select_related('author', 'category').prefetch_related('tags').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/tag_detail.html', {
        'tag': tag,
        'page_obj': page_obj,
        'posts': page_obj
    })


def search(request):
    """Search posts by title, content, category, and tags"""
    query = request.GET.get('q', '').strip()
    results = []
    count = 0
    
    if query:
        # Search in title, content, category name, and tag names
        posts = Post.objects.filter(
            status='published'
        ).filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).select_related('author', 'category').prefetch_related('tags').distinct().order_by('-created_at')
        
        count = posts.count()
        
        # Pagination
        paginator = Paginator(posts, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = None
    
    return render(request, 'blog/search_results.html', {
        'query': query,
        'page_obj': page_obj,
        'count': count
    })


def latest_posts_view(request):
    """Display all latest posts with pagination"""
    # Get featured post IDs to exclude
    featured_ids = list(Post.objects.filter(
        status='published',
        is_featured=True
    ).values_list('id', flat=True))
    
    posts = Post.objects.filter(
        status='published'
    ).exclude(id__in=featured_ids).select_related('author', 'category').prefetch_related('tags').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/posts_list.html', {
        'page_obj': page_obj,
        'posts': page_obj,
        'title': 'Latest Posts',
        'subtitle': 'All the latest posts from our community',
        'icon': 'newspaper'
    })


def recent_posts_view(request):
    """Display all recent posts (last 7 days) with pagination"""
    # Get featured post IDs to exclude
    featured_ids = list(Post.objects.filter(
        status='published',
        is_featured=True
    ).values_list('id', flat=True))
    
    seven_days_ago = timezone.now() - timedelta(days=7)
    posts = Post.objects.filter(
        status='published',
        created_at__gte=seven_days_ago
    ).exclude(id__in=featured_ids).select_related('author', 'category').prefetch_related('tags').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/posts_list.html', {
        'page_obj': page_obj,
        'posts': page_obj,
        'title': 'Recently Uploaded',
        'subtitle': 'Posts from the last 7 days',
        'icon': 'clock'
    })


def most_liked_posts_view(request):
    """Display all most liked posts with pagination"""
    # Get featured post IDs to exclude
    featured_ids = list(Post.objects.filter(
        status='published',
        is_featured=True
    ).values_list('id', flat=True))
    
    posts = Post.objects.filter(
        status='published'
    ).exclude(id__in=featured_ids).select_related('author', 'category').prefetch_related('tags').order_by('-like_count', '-created_at')
    
    # Pagination
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/posts_list.html', {
        'page_obj': page_obj,
        'posts': page_obj,
        'title': 'Most Liked Posts',
        'subtitle': 'Popular posts loved by the community',
        'icon': 'heart'
    })


def about_view(request):
    """Display about page with website information and features"""
    # Get some stats for the about page
    total_posts = Post.objects.filter(status='published').count()
    total_authors = User.objects.filter(post__status='published').distinct().count()
    total_categories = Category.objects.count()
    total_tags = Tag.objects.count()
    
    return render(request, 'blog/about.html', {
        'total_posts': total_posts,
        'total_authors': total_authors,
        'total_categories': total_categories,
        'total_tags': total_tags,
    })


def like_toggle(request, slug):
    """Toggle like on a post (AJAX or redirect)"""
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax')
    
    # For AJAX requests, return JSON error if not authenticated
    if not request.user.is_authenticated:
        if is_ajax:
            return JsonResponse({'error': 'Authentication required. Please log in.'}, status=401)
        return redirect('accounts:login')
    
    if request.method != 'POST':
        if is_ajax:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        return redirect('blog:post_detail', slug=slug)
    
    post = get_object_or_404(Post, slug=slug)
    
    # Allow likes on published posts or user's own posts
    if post.status != 'published' and post.author != request.user:
        if is_ajax:
            return JsonResponse({'error': 'Cannot like this post'}, status=403)
        messages.error(request, 'Cannot like this post.')
        return redirect('blog:post_list')
    
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        # Unlike
        like.delete()
        liked = False
        # Update like_count
        post.like_count = max(0, post.like_count - 1)
        post.save(update_fields=['like_count'])
    else:
        # Like
        liked = True
        # Update like_count
        post.like_count += 1
        post.save(update_fields=['like_count'])
    
    # Return JSON for AJAX requests
    if is_ajax:
        return JsonResponse({
            'liked': liked,
            'like_count': post.likes.count()
        })
    
    # Otherwise redirect back
    return redirect('blog:post_detail', slug=post.slug)


@login_required
def comment_create(request, slug):
    """Create a comment on a post"""
    post = get_object_or_404(Post, slug=slug)
    
    # Allow comments on published posts or user's own posts
    if post.status != 'published' and post.author != request.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Cannot comment on this post.'}, status=403)
        messages.error(request, 'Cannot comment on this post.')
        return redirect('blog:post_list')
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            
            # Handle reply to another comment
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id, post=post)
                    comment.parent = parent_comment
                except Comment.DoesNotExist:
                    pass
            
            comment.save()
            
            # Return JSON for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.utils.html import escape
                from django.template.defaultfilters import linebreaksbr
                return JsonResponse({
                    'success': True,
                    'comment_id': comment.id,
                    'author': comment.author.username,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%B %d, %Y'),
                    'is_reply': comment.parent is not None,
                    'parent_id': comment.parent.id if comment.parent else None
                })
            
            messages.success(request, 'Comment added successfully!')
            return HttpResponseRedirect(f"{reverse('blog:post_detail', kwargs={'slug': post.slug})}#comments")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Please correct the errors in your comment.', 'errors': form.errors}, status=400)
            messages.error(request, 'Please correct the errors in your comment.')
    
    return redirect('blog:post_detail', slug=post.slug)


@login_required
def comment_edit(request, slug, comment_id):
    """Edit a comment"""
    post = get_object_or_404(Post, slug=slug)
    comment = get_object_or_404(Comment, id=comment_id, post=post)
    
    # Check if user is the author
    if comment.author != request.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'You can only edit your own comments.'}, status=403)
        messages.error(request, 'You can only edit your own comments.')
        return redirect('blog:post_detail', slug=post.slug)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            
            # Return JSON for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'content': comment.content,
                    'comment_id': comment.id
                })
            
            messages.success(request, 'Comment updated successfully!')
            return HttpResponseRedirect(f"{reverse('blog:post_detail', kwargs={'slug': post.slug})}#comments")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Please correct the errors.', 'errors': form.errors}, status=400)
            messages.error(request, 'Please correct the errors.')
    
    return redirect('blog:post_detail', slug=post.slug)