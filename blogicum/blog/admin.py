"""Настройка отображения моделей Category, Location и Post в админке."""

from django.contrib import admin

from .models import Category, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'description', 'is_published'
    )
    list_editable = ('is_published',)
    list_filter = ('is_published',)


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'is_published'
    )
    list_editable = ('is_published',)
    list_filter = ('is_published',)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'category',
        'location', 'pub_date', 'is_published'
    )
    list_editable = ('is_published',)
    list_filter = (
        'pub_date', 'author', 'location',
        'category', 'is_published'
    )
    empty_value_display = 'Не задано'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
