from django.shortcuts import get_object_or_404, render, redirect
from blog.models import Post, Category, Comment
from django.http import Http404
from datetime import datetime as dati

# ДОБАВЛЕНО в 6-ом спринте.
from django.contrib.auth import get_user_model
from .forms import *
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Count

User = get_user_model()
PAGINATOR_PAGES_COUNT = 10

def is_public(query_set):
    return query_set.filter(is_published__exact=True, category__is_published__exact=True)

def comment_calc(query_set):
    return query_set.annotate(
        comment_count=Count('comments')
    )

def get_paginator(request, query_set):
    paginator = Paginator(query_set, PAGINATOR_PAGES_COUNT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

def date_filter(query_set):
    return query_set.filter(pub_date__lte=dati.now()).order_by('-pub_date')

def index(request):
    post_list = date_filter(comment_calc(is_public(Post.objects.select_related(
        'category', 'location', 'author'
    ))))
    post_list_pag = get_paginator(request, post_list)
    context = {'page_obj': post_list_pag}
    return render(request, 'blog/index.html', context)

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        post = get_object_or_404(
            Post,
            id=post_id,
            is_published=True,
            category__is_published=True,
            pub_date__lte=dati.now())
    form = CommentForm(request.POST or None)
    comments = Comment.objects.select_related(
        'author').filter(post=post)
    context = {'post': post,
               'form': form,
               'comments': comments}
    return render(request, 'blog/detail.html', context)

@login_required
def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug__exact=category_slug)
    if not category.is_published:
        raise Http404()
    post_list = date_filter(comment_calc(is_public(category.post.all())))
    post_list_pag = get_paginator(request, post_list)
    context = {
        'page_obj': post_list_pag,
        'category': category
    }
    return render(request, 'blog/category.html', context)

@login_required
def create_post(request):
    form = CreatePostForm(request.POST or None, files=request.FILES or None)
    context = {
        'form': form
    }
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        username = request.user.username
        return redirect('blog:profile', username=username)
    return render(request, 'blog/create.html', context)

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    form = CreatePostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {'form': form}
    return render(request, 'blog/create.html', context)

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    form = CreatePostForm(request.POST or None, instance=post)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    context = {'form': form}
    return render(request, 'blog/create.html', context)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id)

@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {'comment': comment,
               'form': form}
    return render(request, 'blog/comment.html', context)

@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id)
    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)

def profile(request, username):
    profile_user = get_object_or_404(
        User,
        username=username,
    )
    if request.user != profile_user:
        post_list = date_filter(comment_calc(is_public(profile_user.post.all())).order_by('title'))
    else:
        post_list = comment_calc(
            profile_user.post.all()
        ).order_by('title').order_by('-pub_date')
    post_list_pag = get_paginator(request, post_list)
    context = {
        'profile': profile_user,
        'page_obj': post_list_pag,
    }
    return render(request, 'blog/profile.html', context)

@login_required
def edit_profile(request):
    instance = get_object_or_404(User, username__exact=request.user.username)
    form = UserEditForm(request.POST or None, instance=instance)

    context = {
        'form': form
    }
    if form.is_valid():
        form.save()
        username = form.cleaned_data['username']
        return redirect('blog:profile', username=username)
    return render(request, 'blog/user.html', context)