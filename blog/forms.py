from django import forms
from django.utils.text import slugify
from .models import Post, Comment, Category, Tag


class PostForm(forms.ModelForm):
    """Form for creating and editing blog posts"""
    
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., django, python, tutorial (comma-separated, max 3)'
        }),
        help_text='Enter up to 3 tags separated by commas. Tags will be created automatically if they don\'t exist.'
    )
    
    class Meta: 
        model = Post
        fields = ['title', 'content', 'image', 'category', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control quill-editor',
                'rows': 15,
                'placeholder': 'Write your post content here...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'title': 'Post Title',
            'content': 'Content',
            'image': 'Featured Image (optional)',
            'category': 'Category (optional)',
            'tags_input': 'Tags (max 3)',
            'status': 'Status'
        }
        help_texts = {
            'image': 'Upload a featured image for your post.',
            'category': 'Select a category to help organize your post.',
            'tags_input': 'Enter up to 3 tags separated by commas (e.g., django, python, tutorial).',
            'status': 'Draft posts are only visible to you. Published posts are visible to everyone.'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make category optional
        self.fields['category'].required = False
        self.fields['category'].queryset = Category.objects.all().order_by('name')
        
        # Pre-populate tags_input if editing
        if self.instance and self.instance.pk:
            tags = self.instance.tags.all()
            if tags:
                self.fields['tags_input'].initial = ', '.join([tag.name for tag in tags])
    
    def clean_tags_input(self):
        tags_input = self.cleaned_data.get('tags_input', '').strip()
        if not tags_input:
            return ''
        
        # Split by comma, trim, and filter empty
        tag_names = [name.strip() for name in tags_input.split(',') if name.strip()]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in tag_names:
            if tag.lower() not in seen:
                seen.add(tag.lower())
                unique_tags.append(tag)
        
        # Enforce max 3 tags
        if len(unique_tags) > 3:
            raise forms.ValidationError('You can enter a maximum of 3 tags.')
        
        return ', '.join(unique_tags)


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