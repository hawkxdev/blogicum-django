"""Формы для создания и редактирования публикаций и комментариев."""

from django import forms
from django.forms.widgets import DateTimeInput

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования постов."""

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image')
        widgets = {
            'pub_date': DateTimeInput(attrs={'type': 'datetime-local'})
        }


class CommentForm(forms.ModelForm):
    """Форма для добавления и редактирования комментариев."""

    class Meta:
        model = Comment
        fields = ('text',)
