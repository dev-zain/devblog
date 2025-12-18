from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . models import Post, Comment
from . forms import PostForm, CommentForm


def post_list(request):
    """Display list of published blog posts"""
    posts = Post. objects.filter(status='published').order_by('-created_at')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, slug):
    """Display a single blog post"""
    post = get_object_or_404(Post, slug=slug, status='published')
    comments = post. comments.all().order_by('-created_at')
    
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments
    })


@login_required
def post_create(request):
    """Create a new blog post"""
    if request.method == 'POST': 
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('blog:post_detail', slug=post.slug)
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
        messages. error(request, 'You can only edit your own posts!')
        return redirect('blog:post_detail', slug=post.slug)
    
    if request.method == 'POST': 
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/post_form.html', {
        'form': form,
        'title':  'Edit Post',
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
    ).order_by('-created_at')
    
    draft_posts = Post.objects.filter(
        author=request.user,
        status='draft'
    ).order_by('-created_at')
    
    return render(request, 'blog/my_posts.html', {
        'published_posts': published_posts,
        'draft_posts':  draft_posts
    })