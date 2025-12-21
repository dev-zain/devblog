from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('my-posts/', views.my_posts, name='my_posts'),               
    path('post/create/', views.post_create, name='post_create'),     
    path('post/<slug:slug>/', views.post_detail, name='post_detail'), 
    path('post/<slug:slug>/edit/', views.post_edit, name='post_edit'),
    path('post/<slug:slug>/delete/', views.post_delete, name='post_delete'),
    path('post/<slug:slug>/like/', views.like_toggle, name='like_toggle'),
    path('post/<slug:slug>/comment/', views.comment_create, name='comment_create'),
    path('post/<slug:slug>/comment/<int:comment_id>/edit/', views.comment_edit, name='comment_edit'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('tag/<slug:slug>/', views.tag_detail, name='tag_detail'),
    path('search/', views.search, name='search'),
    path('latest/', views.latest_posts_view, name='latest_posts'),
    path('recent/', views.recent_posts_view, name='recent_posts'),
    path('most-liked/', views.most_liked_posts_view, name='most_liked_posts'),
    path('about/', views.about_view, name='about'),
]