from django.shortcuts import render, get_object_or_404
from .models import Post, Group


# def index(request):
#     template = 'posts/index.html'
#     context = {
#         'text': 'Это главная страница проекта Yatube'
#     }
#     return render(request, template, context)


def index(request):
    posts = Post.objects.order_by('-pub_date')[:10]
    context = {
        'posts': posts,
    }
    return render(request, 'posts/index.html', context) 

def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, template, context)
