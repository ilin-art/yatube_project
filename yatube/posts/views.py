from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from yatube.paginator import get_paginator_page

from .models import Post, Group, Follow, User
from .forms import PostForm, CommentForm

from yatube.settings import POSTS_PER_PAGE


def index(request):
    posts = Post.objects.select_related('group')
    page_obj = get_paginator_page(request, posts)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.select_related('group').filter(group=group)
    page_obj = get_paginator_page(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
        'posts': posts,
    }
    return render(request, template, context)


def profile(request, username):
    # Здесь код запроса к модели и создание словаря контекста
    user = get_object_or_404(User, username=username)
    following = (
        request.user.is_authenticated
        and user.following.exists()
    )
    posts = user.posts.all()
    page_obj = get_paginator_page(request, posts)
    context = {
        'page_obj': page_obj,
        'author': user,
        'posts': posts,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect(f'/profile/{request.user}/')
    form = PostForm()
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template_name = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if post.author == request.user:
        if form.is_valid():
            post = form.save()
            return redirect('posts:post_detail', post_id)
        return render(request,
                      template_name,
                      {'form': form, 'is_edit': True})
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Страница с авторами на которых подписаны."""
    follow_posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(follow_posts, POSTS_PER_PAGE)
    page_obj = get_paginator_page(request, follow_posts)
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Делает подписку на автора."""
    author = get_object_or_404(User, username=username)
    follow = author.following
    # Follow.objects.filter(
    #     user=request.user,
    #     author=author)
    if request.user != author and not follow.exists():
        Follow.objects.create(user=request.user,
                              author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    """Делает отписку от автора."""
    author = get_object_or_404(User, username=username)
    user = request.user
    Follow.objects.filter(author=author, user=user).delete()
    return redirect('posts:profile', username)
