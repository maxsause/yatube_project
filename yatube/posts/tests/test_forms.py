from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post

User = get_user_model()


class FormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_form_edit_post(self):
        """Форма edit_post работает правильно"""
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост'
        )
        form_data = {
            'text': 'Тестовый отредактированный текст'
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            form_data, follow=True)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, form_data['text'])
        self.assertEqual(self.post.author.username, self.user.username)

    def test_form_create_post(self):
        """Форма create_post работает правильно"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст'
        }
        response = self.authorized_client.post(
            reverse('posts:create_post'), data=form_data
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
