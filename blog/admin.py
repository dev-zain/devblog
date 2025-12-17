from django.contrib import admin
from .models import Post, Comment   

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'author__username', 'content')
    list_filter = ('status', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    search_fields = ('post__title', 'author__username', 'content')
    list_filter = ('created_at',)

