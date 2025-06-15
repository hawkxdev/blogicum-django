"""View-функции и классы для отображения главной страницы, постов,
категорий и профиля пользователя."""

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

from .models import Category, Post

User = get_user_model()

# Количество постов отображаемых на главной странице
INDEX_POST_LIMIT = 5


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница c пятью последними опубликованными постами."""
    template_name = 'blog/index.html'
    context = {
        'post_list': Post.objects.published()[:INDEX_POST_LIMIT]
    }
    return render(request, template_name, context)


def post_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Страница поста по идентификатору."""
    template_name = 'blog/detail.html'
    post = get_object_or_404(
        Post.objects.published(),
        pk=pk
    )
    context = {
        'post': post
    }
    return render(request, template_name, context)


def category_posts(request: HttpRequest, category_slug: str) -> HttpResponse:
    """Список постов выбранной категории."""
    template_name = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_list_or_404(
        Post.objects.published(),
        category=category
    )
    context = {
        'category': category,
        'post_list': post_list
    }
    return render(request, template_name, context)


class ProfileDetailView(DetailView):
    """Страница профиля пользователя."""
    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'


class PostCreateView(LoginRequiredMixin, CreateView):
    """Страница создания нового поста."""
    model = Post
    fields = '__all__'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:create_post')
