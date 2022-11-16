from . import views
from django.urls import include, path

app_name = 'posts'

urlpatterns = [
    path('auth/', include('django.contrib.auth.urls')),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.post_create, name='create_post'),
    path('', views.index, name='index'),

]
