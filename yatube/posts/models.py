from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
        help_text='Дайте короткое название группе. 200 символов максимум'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Адрес',
        help_text=('Укажите адрес для страницы группы. Используйте только '
                     'латиницу, цифры, дефисы и знаки подчёркивания')
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Дайте описание группе'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата',
        help_text='Автоматически добавляет текущее время'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='При удалении, также удаляет все посты автора'
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
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date', )

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
        help_text='Пост, к которому относится комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
        help_text='При удалении, также удаляет все комментарии автора'
    )
    text = models.TextField(
        verbose_name='Текст',
        help_text='Введите комментарий'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата',
        help_text='Автоматически добавляет текущее время'
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
    )
