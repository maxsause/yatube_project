from . import views
from django.urls import include, path

app_name = 'posts'

urlpatterns = [
    path('auth/', include('django.contrib.auth.urls')),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
    path('create/', views.post_create, name='create_post'),
    path('', views.index, name='index'),
]
