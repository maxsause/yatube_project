from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404

from .forms import CommentForm, PostForm
from .models import Group, Post, User, Follow
from .utils import pagination


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.select_related('author', 'group').all()
    context = {
        'page_obj': pagination(request, posts),
    }
    return render(request, template, context)


def group_posts(request, slug=None):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.all()
    context = {
        'group': group,
        'page_obj': pagination(request, posts),
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    if (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author)
    ):
        following = True
    else:
        following = False
    posts = author.posts.all()
    context = {
        'author': author,
        'following': following,
        'page_obj': pagination(request, posts),
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    author = get_object_or_404(User, username=post.author)
    counter = author.posts.all().count()
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'counter': counter,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    context = {
        'form': form,
        'is_edit': False
    }
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', request.user)
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post.pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save()
        return redirect('posts:post_detail', post.pk)
    context = {
        'post_id': post_id,
        'form': form,
        'is_edit': True
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post.pk)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    list_posts = Post.objects.filter(
        author__following__user=request.user
    ).select_related("author", "group")
    page_obj = pagination(request, list_posts)
    context = {
        "page_obj": page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (
        not User.objects.filter(
            username=author,
            following__user=request.user,
        ).exists()
        and author != request.user
    ):
        Follow.objects.create(user=request.user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    old = Follow.objects.filter(
        user=request.user,
        author=author
    )
    if old.exists():
        old.delete()
    return redirect("posts:profile", username=author)
