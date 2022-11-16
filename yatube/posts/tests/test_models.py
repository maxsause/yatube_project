from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(self.post.text[:15], str(self.post),
                         'название поста не соответствует ожидаемому')

    def test_verbose_name_post(self):
        """verbose_name в полях совпадает с ожидаемым."""
        task_post = PostModelTest.post
        field_verboses_post = {
            'text': 'Текст',
            'pub_date': 'Дата',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task_post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_text_post(self):
        """help_text в полях совпадает с ожидаемым."""
        task_post = PostModelTest.post
        field_help_texts_post = {
            'text': 'Введите текст поста',
            'pub_date': 'Автоматически добавляет текущее время',
            'author': 'При удалении, также удаляет все посты автора',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, expected_value in field_help_texts_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task_post._meta.get_field(field).help_text,
                    expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый адрес',
            description='Тестовое описание',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(self.group.title, str(self.group),
                         'название группы не соответствует ожидаемому')

    def test_verbose_name_group(self):
        """verbose_name в полях совпадает с ожидаемым."""
        task_group = GroupModelTest.group
        field_verboses_group = {
            'title': 'Заголовок',
            'slug': 'Адрес',
            'description': 'Описание'
        }
        for field, expected_value in field_verboses_group.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task_group._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_text_group(self):
        """help_text в полях совпадает с ожидаемым."""
        task_group = GroupModelTest.group
        field_help_texts_group = {
            'title': 'Дайте короткое название группе. 200 символов максимум',
            'slug': ('Укажите адрес для страницы группы. Используйте только '
                     'латиницу, цифры, дефисы и знаки подчёркивания'),
            'description': 'Дайте описание группе'
        }
        for field, expected_value in field_help_texts_group.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task_group._meta.get_field(field).help_text,
                    expected_value)
