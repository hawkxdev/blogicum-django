from django import forms
from .models import Post
from django.forms.widgets import DateTimeInput


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category')
        widgets = {
            'pub_date': DateTimeInput(attrs={'type': 'datetime-local'})
        }
