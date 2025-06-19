"""View-функции и классы для отображения главной страницы, постов,
категорий и профиля пользователя.
"""

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import AbstractBaseUser
from django.core.paginator import Paginator, Page
from django.db.models import Count
from django.http import (Http404, HttpRequest, HttpResponse,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django.db.models import QuerySet

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

User = get_user_model()

# Максимальное количество постов на странице
INDEX_POST_LIMIT = 10


def get_paginator(posts: QuerySet[Post], request: HttpRequest) -> Page:
    """Разбивает посты на страницы и возвращает текущую страницу."""
    paginator = Paginator(posts, INDEX_POST_LIMIT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница: список опубликованных постов
    с разбивкой на страницы.
    """
    posts = Post.objects.published().annotate(comment_count=Count('comments'))
    page_obj = get_paginator(posts, request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'blog/index.html', context)


def post_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Страница поста по идентификатору."""
    post = get_object_or_404(Post, pk=pk)

    if ((not post.is_published or post.pub_date > timezone.now()
         or not post.category.is_published)
            and post.author != request.user):
        raise Http404

    form = CommentForm()
    comments = post.comments.select_related('author')

    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request: HttpRequest, category_slug: str) -> HttpResponse:
    """Список постов выбранной категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = Post.objects.published().filter(category=category)
    page_obj = get_paginator(posts, request)

    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)


class RedirectToPostMixin:
    """Миксин для перенаправления на страницу публикации
    при отсутствии доступа.
    """

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseRedirect(
            reverse('blog:post_detail', kwargs={'pk': self.get_object().pk})
        )


class AuthorRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки что пользователь автор объекта."""

    def test_func(self) -> bool:
        return self.get_object().author == self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Страница редактирования профиля пользователя."""

    model = User
    fields = ('username', 'first_name', 'last_name', 'email')
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self) -> AbstractBaseUser:
        """Возвращает текущего пользователя для редактирования."""
        return self.request.user


class ProfileDetailView(DetailView):
    """Страница профиля пользователя с его публикациями."""

    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.object
        posts = Post.objects.filter(author=user).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
        page_obj = get_paginator(posts, self.request)

        context['page_obj'] = page_obj
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Страница создания нового поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form: PostForm) -> HttpResponse:
        """Устанавливает автора поста перед сохранением."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(RedirectToPostMixin, AuthorRequiredMixin, UpdateView):
    """Страница редактирования поста доступна только автору."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self) -> str:
        post = self.object
        return reverse(
            'blog:post_detail',
            kwargs={'pk': post.pk}
        )


class PostDeleteView(RedirectToPostMixin, AuthorRequiredMixin, DeleteView):
    """Страница удаления поста доступна только автору."""

    model = Post

    def get_success_url(self) -> str:
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание нового комментария к посту доступно только
    авторизованным пользователям.
    """

    post_object: Post | None = None
    form_class = CommentForm

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Получает объект поста и сохраняет его в self.post_object."""
        self.post_object = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: CommentForm) -> HttpResponse:
        """Устанавливает автора и пост перед сохранением комментария."""
        form.instance.post = self.post_object
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', kwargs={'pk': self.post_object.pk})


class CommentUpdateView(RedirectToPostMixin, AuthorRequiredMixin, UpdateView):
    """Редактирование комментария доступно только автору."""

    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk})


class CommentDeleteView(RedirectToPostMixin, AuthorRequiredMixin, DeleteView):
    """Удаление комментария доступно только автору."""

    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk})
