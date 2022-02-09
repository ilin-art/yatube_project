from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

import tempfile
import shutil

from .. models import Post, Group, Comment, User
from .. forms import CommentForm


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем запись в базе данных
        cls.user_author = User.objects.create_user(username='user_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='some.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Текст',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        # Создаем авторизованый клиент, который также автор поста
        self.post_author = Client()
        self.post_author.force_login(self.user_author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Task
        posts_count = Post.objects.count()
        form_data = {
            'title': 'Тестовый заголовок 3',
            'text': 'Тестовый текст 3',
            'image': self.post.image,
        }
        # Отправляем POST-запрос
        response = self.post_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user_author}
        ))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись
        self.assertTrue(
            Post.objects.filter(
                author=PostFormTest.user_author,
                text='Текст',
                group=PostFormTest.group,
                image='posts/some.gif'
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма обновляет выбранный пост."""
        post = PostFormTest.post
        form_data = {
            'text': 'Новый текст',
        }
        response = self.post_author.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        post.refresh_from_db()
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post.id})
        )
        self.assertEqual(post.text, 'Новый текст')


class TestCommentForm(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
        )
        cls.form = CommentForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_add_comment(self):
        """Валидная форма добавляет комментарий к выбранному посту."""
        post = TestCommentForm.post
        form_data = {
            'text': 'Текст комментария',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post.id})
        )
        comment = Comment.objects.first()
        # Проверяем, появился ли комментарий
        self.assertEqual(comment.text, 'Текст комментария')
        # Проверяем, появился ли комментарий в контексте шаблона post_detail
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        self.assertIn(comment, response.context.get('comments'))

    def test_anonymous_cant_add_comment(self):
        """Анонимный пользователь не может добавить комментарий."""
        post = TestCommentForm.post
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Текст гостя',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        # Проверяем, что при попытке добавить комментарий
        # кол-во комментариев остается прежним
        self.assertEqual(Comment.objects.count(), comments_count)
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')
