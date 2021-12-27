from django.shortcuts import render, get_object_or_404
from .models import Post, Group
SORT_POST = 10


def index(request):
    posts = Post.objects.select_related('group')[:SORT_POST]
    context = {
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.select_related('group').filter(group=group)[:SORT_POST]
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, template, context)
