import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTest(TestCase):
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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
            'text': 'Тестовый текст',
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:create_post'), data=form_data
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_form_comment(self):
        """Форма comment работает правильно"""
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост'
        )
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст'
        }
        post_id = self.post.pk
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post_id}),
            data=form_data
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post_id}
        ))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
