from django.shortcuts import render, get_object_or_404
from .models import Post, Comment

def post_list(request):
    posts = Post.objects.filter(status='published').order_by('-created_at')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    comments = post.comments.all().order_by('created_at')
    context = {
        'post': post,
        'comments': comments
        }
    return render(request, 'blog/post_detail.html', context)

