from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import Post, Comment, Category, Location

User = get_user_model()


class CustomCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class PostForm(forms.ModelForm):
    # Новые поля для ввода текста
    new_category = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите название новой категории'
        }),
        label='Или создайте новую категорию'
    )
    
    new_location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите новое местоположение'
        }),
        label='Или создайте новое местоположение'
    )
    
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'location': forms.Select(attrs={
                'class': 'form-control',
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'is_published': 'Опубликовать сейчас',
            'pub_date': 'Дата и время публикации',
            'text': 'Текст поста',
            'title': 'Заголовок',
            'location': 'Местоположение',
            'category': 'Категория',
            'image': 'Изображение',
        }
        help_texts = {
            'is_published': 'Снимите галочку, чтобы скрыть публикацию.',
            'pub_date': 'Если выбрать дату и время в будущем, то публикация будет отложенной.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pub_date'].required = False
        self.fields['image'].widget.attrs.update({'class': 'form-control'})
        self.fields['category'].required = False
        self.fields['location'].required = False
        
        self.fields['category'].queryset = Category.objects.filter(is_published=True)
        self.fields['location'].queryset = Location.objects.all()
        
        if not self.instance.pk:
            from django.utils import timezone
            self.fields['pub_date'].initial = timezone.now()
    
    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_category = cleaned_data.get('new_category')
        location = cleaned_data.get('location')
        new_location = cleaned_data.get('new_location')
        
        if not category and not new_category:
            raise forms.ValidationError(
                'Выберите категорию из списка или введите новую'
            )
        
        if category and new_category:
            cleaned_data['new_category'] = ''
        
        if not location and not new_location:
            raise forms.ValidationError(
                'Выберите местоположение из списка или введите новое'
            )
        
        if location and new_location:
            cleaned_data['new_location'] = ''
        
        return cleaned_data
    
    def save(self, commit=True):
        post = super().save(commit=False)
        
        new_category = self.cleaned_data.get('new_category')
        if new_category and not self.cleaned_data.get('category'):
            from django.utils.text import slugify
            slug = slugify(new_category)
            counter = 1
            original_slug = slug
            while Category.objects.filter(slug=slug).exists():
                slug = f'{original_slug}-{counter}'
                counter += 1
            
            category = Category.objects.create(
                title=new_category,
                slug=slug,
                description=f'Категория "{new_category}"',
                is_published=True
            )
            post.category = category
        new_location = self.cleaned_data.get('new_location')
        if new_location and not self.cleaned_data.get('location'):
            location = Location.objects.create(name=new_location)
            post.location = location
        
        if commit:
            post.save()
        return post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
            }),
        }