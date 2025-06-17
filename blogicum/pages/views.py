"""Обработчики статических страниц и системных ошибок проекта."""

from django.shortcuts import render
from django.views.generic import TemplateView


class AboutPage(TemplateView):
    """Отображает статическую страницу "О проекте"."""
    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    """Отображает статическую страницу "Правила"."""
    template_name = 'pages/rules.html'


def csrf_failure(request, reason=''):
    """Обработка ошибки CSRF: подделка межсайтового запроса."""
    _ = reason
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    """Обработка ошибки 404: страница не найдена."""
    _ = exception
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Обработка ошибки 500: внутренняя ошибка сервера."""
    return render(request, 'pages/500.html', status=500)
