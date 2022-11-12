from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='title',
        help_text='200 characters max.'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='slug',
        help_text=''
    )
    description = models.TextField(
        verbose_name='description',
        help_text='Description of the group'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='date',
        help_text='Auto adds current time.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='author',
        help_text='When deleted, also deletes all the users messages'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='group_posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )

    class Meta:
        ordering = ('-pub_date', )

    def __str__(self):
        return self.text[:15]
