from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.paginator import BuildPaginator

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    posts = Post.objects.select_related('author', 'group')
    template = "posts/index.html"
    title = "Это главная страница проекта Yatube"

    context = {
        "title": title,
        "page_obj": BuildPaginator.get_page_obj(
            request, posts, settings.POST_PER_PAGE)
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    template = "posts/group_list.html"

    context = {
        "group": group,
        "page_obj": BuildPaginator.get_page_obj(
            request, posts, settings.POST_PER_PAGE),
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    users_posts = author.posts.select_related("group")

    is_follower = (request.user.is_authenticated and
                   request.user != author and author.following.exists())
    context = {
        "author": author,
        "count_of_posts": BuildPaginator.get_paginator_count(
         users_posts, settings.POST_PER_PAGE),
        "users_posts": users_posts,
        "page_obj": BuildPaginator.get_page_obj(
            request, users_posts, settings.POST_PER_PAGE),
        "is_follower": is_follower,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related(
            "author", "group").prefetch_related("author"), pk=post_id
    )
    form = CommentForm()
    context = {
        "post": post,
        "count_posts": post.author.posts.count(),
        "form": form,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", username=post.author.username)
    context = {
        "form": form,
        "title": "Добавить запись",
        "is_edit": False
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author == request.user:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
        context = {
            "is_edit": True,
            "title": "Редактировать запись",
            "form": form
        }
        return render(request, "posts/create_post.html", context)
    return redirect("posts:post_detail", post_id=post_id)


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
    post_list = Post.objects.filter(author__following__user=request.user)
    context = {
        "page_obj": BuildPaginator.get_page_obj(
            request, post_list, settings.POST_PER_PAGE
        ),
        "is_no_following": BuildPaginator.get_paginator_count(
            post_list, settings.POST_PER_PAGE) == 0,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    is_follower = author.following
    if request.user != author and not is_follower.exists():
        Follow.objects.create(user=request.user, author=author)
    return redirect("posts:profile", username=author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    is_follower = author.following.filter(author=author)
    is_follower.delete()
    return redirect("posts:profile", username=author)
