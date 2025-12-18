from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Form for creating and editing blog posts"""
    
    class Meta: 
        model = Post
        fields = ['title', 'content', 'image', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':  'Enter post title'
            }),
            'content': forms. Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Write your post content here...'
            }),
            'image': forms. FileInput(attrs={
                'class': 'form-control'
            }),
            'status':  forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'title': 'Post Title',
            'content': 'Content',
            'image': 'Featured Image (optional)',
            'status': 'Status'
        }
        help_texts = {
            'image': 'Upload a featured image for your post.',
            'status': 'Draft posts are only visible to you.  Published posts are visible to everyone.'
        }


class CommentForm(forms.ModelForm):
    """Form for adding comments to blog posts"""
    
    class Meta: 
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms. Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment...'
            })
        }
        labels = {
            'content': 'Comment'
        }