"""Настройка отображения моделей Category, Location, Post
и Comment в админке.
"""

from django.contrib import admin
from django.template.defaultfilters import truncatechars
from django.utils.html import format_html

from .models import Category, Comment, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'description', 'is_published',
    )
    list_editable = ('is_published',)
    list_filter = ('is_published',)


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'is_published',
    )
    list_editable = ('is_published',)
    list_filter = ('is_published',)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'category',
        'location', 'pub_date', 'is_published',
    )
    list_editable = ('is_published',)
    list_filter = (
        'pub_date', 'author', 'location',
        'category', 'is_published',
    )
    empty_value_display = 'Не задано'


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'post', 'author', 'short_text_html', 'created_at'
    )
    list_display_links = ('short_text_html',)

    def short_text_html(self, comment) -> str:
        """Возвращает укороченную версию текста комментария
        с безопасным HTML-выводом для отображения в админке.
        """
        return format_html('{}', truncatechars(comment.text, 50))

    short_text_html.short_description = 'Текст комментария'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
