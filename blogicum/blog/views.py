"""View-функции и классы для отображения главной страницы, постов,
категорий и профиля пользователя."""

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import AbstractBaseUser
from django.core.paginator import Paginator
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django.utils.timezone import now
from django.db.models import Count

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

User = get_user_model()

# Максимальное количество постов на странице
INDEX_POST_LIMIT = 10


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница: список опубликованных постов
    с разбивкой на страницы."""
    posts = Post.objects.published().annotate(comment_count=Count('comments'))
    paginator = Paginator(posts, INDEX_POST_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template_name = 'blog/index.html'
    context = {
        'page_obj': page_obj
    }
    return render(request, template_name, context)


def post_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Страница поста по идентификатору."""
    template_name = 'blog/detail.html'
    post = get_object_or_404(Post, pk=pk)

    if not post.is_published or post.pub_date > now():
        if post.author != request.user:
            raise Http404

    form = CommentForm()

    comments = post.comments.select_related('author')

    context = {
        'post': post,
        'form': form,
        'comments': comments,
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
    # Не используем get_list_or_404 так как нужна страница даже без постов
    posts = Post.objects.published().filter(category=category)

    paginator = Paginator(posts, INDEX_POST_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, template_name, context)


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
        paginator = Paginator(posts, INDEX_POST_LIMIT)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
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


class PostUpdateView(UserPassesTestMixin, UpdateView):
    """Страница редактирования поста. Доступна только автору поста."""

    model = Post
    form_class = PostForm

    def test_func(self) -> bool | None:
        post = self.get_object()
        return post.author == self.request.user

    def get_success_url(self) -> str:
        post = self.object
        return reverse(
            'blog:post_detail',
            kwargs={'pk': post.pk}
        )


class PostDeleteView(UserPassesTestMixin, DeleteView):
    """Страница удаления поста. Доступна только автору поста."""

    model = Post

    def get_success_url(self) -> str:
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание нового комментария к посту. Доступно только
    авторизованным пользователям."""

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


class CommentUpdateView(UserPassesTestMixin, UpdateView):
    """Редактирование комментария. Доступно только автору комментария."""

    model = Comment

    def test_func(self) -> bool:
        """Проверяет, что пользователь - автор комментария."""
        comment = self.get_object()
        return comment.author == self.request.user


class CommentDeleteView(UserPassesTestMixin, DeleteView):
    """Страница удаления комментария. Доступна только автору."""

    model = Comment

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk})
