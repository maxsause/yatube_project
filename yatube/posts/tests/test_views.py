import shutil
import tempfile

from django import forms
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, Follow

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
TEMP_CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT, CACHES=TEMP_CACHES)
class PagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            image=cls.uploaded,
        )
        cls.post_with_group = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
            reverse('posts:create_post'): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author.username, self.user.username)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.image.size, self.uploaded.size)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        group = response.context['group']
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.description, self.group.description)

        post = response.context['page_obj'][0]
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.image.size, self.uploaded.size)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(response.context['author'].username,
                         self.user.username)

        post = response.context['page_obj'][0]
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.image.size, self.uploaded.size)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(response.context['counter'], Post.objects.count())
        post = response.context['post']
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.image.size, self.uploaded.size)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(response.context['is_edit'], True)
        self.assertEqual(response.context['post_id'], self.post.pk)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:create_post'))
        self.assertEqual(response.context['is_edit'], False)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


@override_settings(CACHES=TEMP_CACHES)
class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_index_cache(self):
        """Кэш на странице index работает правильно"""
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        response = self.authorized_client.get(reverse('posts:index'))
        old_posts = response.content
        post.delete()
        posts = response.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        new_posts = response.content
        self.assertEqual(old_posts, new_posts)


@override_settings(CACHES=TEMP_CACHES)
class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.author = User.objects.create_user(username='Author')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_follow(self):
        """Подписка работает корректно"""
        follow_count = Follow.objects.count()
        response = self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.author.username}
        ))
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.author.username}
        ))
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_unfollow(self):
        """Отписка работает корректно"""
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.author.username}
        ))
        follow_count = Follow.objects.count()
        response = self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': self.author.username}
        ))
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.author.username}
        ))
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_follow_posts(self):
        """Посты подписок показываются правильно"""
        old_post = Post.objects.create(
            author=self.author,
            text='Тестовый пост',
        )
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.author.username}
        ))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        post = response.context['post']
        self.assertEqual(old_post.text, post.text)

    def test_unfollow_post(self):
        """Посты авторов не показываются не подписавшимся"""
        Post.objects.create(
            author=self.author,
            text='Тестовый пост',
        )
        old_response = self.authorized_client.get(reverse('posts:index'))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotEqual(old_response.content, response.content)


@override_settings(CACHES=TEMP_CACHES)
class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        count_test_posts = settings.PAGINATOR_POSTS_PER_PAGE + 1
        cls.second_page = count_test_posts - settings.PAGINATOR_POSTS_PER_PAGE
        cls.posts = Post.objects.bulk_create([
            Post(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group
            ) for i in range(count_test_posts)
        ])

    def test_first_page_contains_ten_records_index(self):
        """Paginator в index корректно отображает первую страницу"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']),
                         settings.PAGINATOR_POSTS_PER_PAGE)

    def test_second_page_contains_three_records_index(self):
        """Paginator в index корректно отображает вторую страницу"""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), self.second_page)

    def test_first_page_contains_ten_records_group_list(self):
        """Paginator в group_list корректно отображает первую страницу"""
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(len(response.context['page_obj']),
                         settings.PAGINATOR_POSTS_PER_PAGE)

    def test_second_page_contains_three_records_group_list(self):
        """Paginator в group_list корректно отображает вторую страницу"""
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
            + '?page=2')
        self.assertEqual(len(response.context['page_obj']), self.second_page)

    def test_first_page_contains_ten_records_profile(self):
        """Paginator в profile корректно отображает первую страницу"""
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(len(response.context['page_obj']),
                         settings.PAGINATOR_POSTS_PER_PAGE)

    def test_second_page_contains_three_records_profile(self):
        """Paginator в profile корректно отображает вторую страницу"""
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
            + '?page=2')
        self.assertEqual(len(response.context['page_obj']), self.second_page)
