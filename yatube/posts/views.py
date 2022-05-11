
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from yatube.settings import POST_PER_PAGE  # К-во постов на страницу

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


@cache_page(20)
def index(request):
    posts = Post.objects.select_related('author', 'group')
    template = "posts/index.html"
    title = "Это главная страница проекта Yatube"

    paginator = Paginator(posts, POST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "title": title,
        "posts": posts,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    template = "posts/group_list.html"

    paginator = Paginator(posts, POST_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "group": group,
        "posts": posts,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    users_posts = author.posts.select_related("group")

    paginator = Paginator(users_posts, POST_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        is_follower = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        is_follower = False

    is_not_current_user = author != request.user
    count_of_posts = paginator.count

    context = {
        "author": author,
        "count_of_posts": count_of_posts,
        "users_posts": users_posts,
        "page_obj": page_obj,
        "following": is_follower,
        "is_not_current_user": is_not_current_user,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("author", "group"), pk=post_id
    )
    comments = post.comments.all()
    count_posts = post.author.posts.count()
    form = CommentForm()
    context = {
        "post": post,
        "count_posts": count_posts,
        "form": form,
        "comments": comments
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
            post = form.save(commit=False)
            post.save()
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
    # информация о текущем пользователе доступна в переменной request.user
    post_list = Post.objects.filter(author__following__user=request.user)

    paginator = Paginator(post_list, POST_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    # Переменная is_no_following выводит сообщение
    # об отсутствии подписок на авторов
    is_no_following = len(page_obj) == 0
    context = {
        "page_obj": page_obj,
        "is_no_following": is_no_following,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if request.user != author and not is_follower.exists():
        Follow.objects.create(user=request.user, author=author)
    return redirect("posts:profile", username=author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return redirect("posts:profile", username=author)
