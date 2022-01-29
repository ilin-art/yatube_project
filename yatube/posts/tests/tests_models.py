from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
            group=cls.group
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_post_text_help_text(self):
        """help_text поля post.text совпадает с ожидаемым."""
        post = PostModelTest.post
        # Получаем из свойста класса Task значение verbose_name для title
        help_text = post._meta.get_field('text').help_text
        self.assertEqual(help_text, 'Введите текст поста')

    def test_post_author_label(self):
        """verbose_name поля post.author совпадает с ожидаемым."""
        post = PostModelTest.post
        # Получаем из свойста класса Task значение verbose_name для title
        verbose = post._meta.get_field('author').verbose_name
        self.assertEqual(verbose, 'Автор')

    def test_post_group_help_text(self):
        """help_text поля post.group совпадает с ожидаемым."""
        post = PostModelTest.post
        # Получаем из свойста класса Task значение verbose_name для title
        help_text = post._meta.get_field('group').help_text
        self.assertEqual(help_text, 'Выберите группу')

    def test_post_group_label(self):
        """verbose_name поля post.group совпадает с ожидаемым."""
        post = PostModelTest.post
        # Получаем из свойста класса Task значение verbose_name для title
        verbose = post._meta.get_field('group').verbose_name
        self.assertEqual(verbose, 'Группа')
