from django import forms
from django.contrib.auth import get_user_model

from blog.models import Post, Comment
User = get_user_model()

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image', 'is_published')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)