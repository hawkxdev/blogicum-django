from django.urls import path

from . import views
from .views import (CommentCreateView, CommentUpdateView, CommentDeleteView,
                    PostCreateView, PostDeleteView, PostUpdateView,
                    ProfileDetailView, ProfileUpdateView)

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path(
        'posts/create/',
        PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:pk>/edit/',
        PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:pk>/delete/',
        PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:pk>/comment/',
        CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:pk>/edit_comment/<int:comment_pk>/',
        CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:pk>/delete_comment/<int:comment_pk>/',
        CommentDeleteView.as_view(),
        name='delete_comment'
    ),
    path(
        'posts/<int:pk>/',
        views.post_detail,
        name='post_detail'
    ),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'
    ),
    path(
        'profile/edit/',
        ProfileUpdateView.as_view(),
        name='edit_profile'
    ),
    path(
        'profile/<str:username>/',
        ProfileDetailView.as_view(),
        name='profile'
    ),
]
