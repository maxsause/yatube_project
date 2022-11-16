from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404

from .forms import PostForm
from .models import Group, Post, User
from .utils import pagination


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
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
    posts = author.posts.all()
    context = {
        'author': author,
        'page_obj': pagination(request, posts),
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    author = get_object_or_404(User, username=post.author)
    counter = author.posts.all().count()
    context = {
        'post': post,
        'counter': counter,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None)
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
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        post = form.save()
        return redirect('posts:post_detail', post.pk)
    context = {
        'post_id': post_id,
        'form': form,
        'is_edit': True
    }
    return render(request, template, context)
