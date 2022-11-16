from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post

User = get_user_model()


class PagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.post_with_group = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

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

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(response.context['group'].title,
                         self.group.title)
        self.assertEqual(response.context['group'].slug,
                         self.group.slug)
        self.assertEqual(response.context['group'].description,
                         self.group.description)

        self.assertEqual(response.context['page_obj'][0].text, self.post.text)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(response.context['author'].username,
                         self.user.username)
        self.assertEqual(response.context['page_obj'][0].text,
                         self.post.text)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(response.context['post'].text, self.post.text)
        self.assertEqual(response.context['counter'], Post.objects.count())

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(response.context['is_edit'], True)
        self.assertEqual(response.context['post_id'], self.post.pk)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
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
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


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
        while count_test_posts > 0:
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group
            )
            count_test_posts -= 1

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
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        self.assertEqual(len(response.context['page_obj']),
                         settings.PAGINATOR_POSTS_PER_PAGE)

    def test_second_page_contains_three_records_group_list(self):
        """Paginator в group_list корректно отображает вторую страницу"""
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            + '?page=2')
        self.assertEqual(len(response.context['page_obj']), self.second_page)

    def test_first_page_contains_ten_records_profile(self):
        """Paginator в profile корректно отображает первую страницу"""
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': 'auth'}))
        self.assertEqual(len(response.context['page_obj']),
                         settings.PAGINATOR_POSTS_PER_PAGE)

    def test_second_page_contains_three_records_profile(self):
        """Paginator в profile корректно отображает вторую страницу"""
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': 'auth'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), self.second_page)
