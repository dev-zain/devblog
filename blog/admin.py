from django.contrib import admin
from .models import Post, Comment, Category, Tag, Like

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'is_featured', 'like_count', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'author__username', 'content')
    list_filter = ('status', 'is_featured', 'category', 'tags', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_editable = ('is_featured', 'status')
    filter_horizontal = ('tags',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username', 'post__title')
    list_filter = ('created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'parent', 'created_at')
    search_fields = ('post__title', 'author__username', 'content')
    list_filter = ('created_at', 'parent')
    readonly_fields = ('created_at', 'updated_at')

