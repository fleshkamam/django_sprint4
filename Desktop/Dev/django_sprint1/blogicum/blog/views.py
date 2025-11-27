from django.shortcuts import get_object_or_404, render
from blog.models import Post, Category
from django.http import Http404
from datetime import datetime as dati


def index(request):
    post_list = Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        pub_date__lte=dati.now(),
        is_published__exact=True,
        category__is_published__exact=True
    ).order_by('-pub_date')[:5]
    context = {'post_list': post_list}
    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    post = Post.objects.filter(pk=id)
    post_filtered = get_object_or_404(
        post,
        pub_date__lte=dati.now(),
        is_published__exact=True,
        category__is_published__exact=True
    )
    context = {'post': post_filtered}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug__exact=category_slug)
    if not category.is_published:
        raise Http404()
    post_list = category.post.all().filter(
        pub_date__lte=dati.now(),
        is_published__exact=True,
    )
    context = {
        'post_list': post_list,
        'category': category
    }
    return render(request, 'blog/category.html', context)
