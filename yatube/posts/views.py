from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Post, Group
# Create your views here.


def index(request):
    template = 'posts/index.html'
    title = 'Группы'
    posts = Post.objects.order_by('-pub_date')[:10]
    context = {
        'title': title,
        'posts': posts,
    }
    return render(request, template, context)


def group_posts(request, slug=None):
    template = 'posts/group_list.html'
    title = 'Здесь будет информация о группах проекта Yatube'

    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    context = {
        'title': title,
        'group': group,
        'posts': posts,
    }
    return render(request, template, context)

