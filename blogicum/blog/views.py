"""View-функции для отображения главной страницы, постов и категорий"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render

from .models import Category, Post

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
