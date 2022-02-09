from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

import tempfile
import shutil

from ..models import Post, Group, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
        cls.user_author = User.objects.create_user(username='user_author')
        cls.user_author_2 = User.objects.create_user(username='user_author_2')
        cls.user_nonauthor = User.objects.create_user(
            username='user_nonauthor'
        )
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
            text='Тестовый пост',
            group=cls.group,
            image=uploaded,
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2',
        )
        small_gif_2 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_2 = SimpleUploadedFile(
            name='some_2.gif',
            content=small_gif_2,
            content_type='image/gif'
        )
        cls.post_2 = Post.objects.create(
            author=cls.user_author_2,
            text='Тестовый пост 2',
            group=cls.group_2,
            image=uploaded_2,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.unauthorized_user = Client()
        self.post_author = Client()
        self.post_author.force_login(self.user_author)
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user_nonauthor)
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        self.templates_pages_names = {
            reverse('posts:main'): 'posts/index.html',
            reverse(
                'posts:profile', kwargs={'username': 'user_author'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post.id}'}
            ): 'posts/post_detail.html',
            reverse(
                'posts:group', kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post.id}'}
            ): 'posts/create_post.html',
        }
        # Контекст для шаблона index
        response_index = self.post_author.get(reverse('posts:main'))
        first_object_index = response_index.context['page_obj'][0]
        post_text = first_object_index.text
        post_group = first_object_index.group.title
        post_author = first_object_index.author.username
        self.post_image_0 = first_object_index.image
        if response_index.context['page_obj'][0].text == 'Тестовый пост':
            self.values_index = {
                post_text: 'Тестовый пост',
                post_group: 'Тестовая группа',
                post_author: 'user_author',
            }
        else:
            self.values_index = {
                post_text: 'Тестовый пост 2',
                post_group: 'Тестовая группа 2',
                post_author: 'user_author_2',
            }
        # Контекст для шаблона group_list
        response_group_list = self.authorized_user.get(reverse(
            'posts:group', kwargs={'slug': self.group.slug}
        ))
        first_post = response_group_list.context['page_obj'][0]
        post_group = first_post.group.title
        post_author = first_post.author.username
        post_text = first_post.text
        self.post_image_group = first_post.image
        self.values_group_list = {
            post_text: 'Тестовый пост',
            post_group: 'Тестовая группа',
            post_author: 'user_author',
        }
        # Контекст для шаблона profile
        response_profile = self.authorized_user.get(reverse(
            'posts:profile', kwargs={'username': self.user_author}
        ))
        first_object = response_profile.context['page_obj'][0]
        post_text = first_object.text
        post_group = first_object.group.title
        post_author = first_object.author.username
        self.post_image_profile = first_object.image
        self.values_profile = {
            post_text: 'Тестовый пост',
            post_group: 'Тестовая группа',
            post_author: 'user_author',
        }
        # Контекст для шаблона post_detail
        response_post_detail = self.post_author.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}
        ))
        first_obj = response_post_detail.context.get('post')
        self.post_0 = first_obj.text
        self.post_image_detail = first_object.image
        # Контекст для шаблона post_create
        self.response_create = self.authorized_user.get(
            reverse('posts:post_create')
        )
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        self.form_fields_create = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        # Контекст для шаблона post_edit
        self.response_edit = self.post_author.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'})
        )
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        self.form_fields_edit = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        # Страницы для test_post_show_on_third_pages
        self.response_index_post_show = self.authorized_user.get("/")
        self.response_group_list_post_show = (
            self.authorized_user.get("/group/test-slug/")
        )
        self.response_profile_post_show = (
            self.authorized_user.get("/profile/user_author/")
        )
        # Контекст второй тестовой группы
        self.response_group_2 = self.authorized_user.get(
            reverse('posts:group', kwargs={'slug': 'test-slug-2'})
        )
        cache.clear()

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Проверяем, что при обращении к name вызывается
        # соответствующий HTML-шаблон
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.post_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        for key, value in self.values_index.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)
        # Проверяем наличие картинки в посте
        self.assertEqual(self.post_image_0, 'posts/some_2.gif')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        for key, value in self.values_group_list.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)
        # Проверяем наличие картинки в посте
        self.assertEqual(self.post_image_group, 'posts/some.gif')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным
        контекстом."""
        for key, value in self.values_profile.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)
        # Проверяем наличие картинки в посте
        self.assertEqual(self.post_image_profile, 'posts/some.gif')

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        self.assertEqual(self.post_0, self.post.text)
        self.assertEqual(self.post_image_detail, 'posts/some.gif')

    def test_create_page_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        # Проверяем, что типы полей формы в словаре
        # context соответствуют ожиданиям
        for value, expected in self.form_fields_create.items():
            with self.subTest(value=value):
                form_field = (
                    self.response_create.context.get('form').fields.get(value)
                )
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_edit_page_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        # Проверяем, что типы полей формы в словаре
        # context соответствуют ожиданиям
        for value, expected in self.form_fields_edit.items():
            with self.subTest(value=value):
                form_field = (
                    self.response_edit.context.get('form').fields.get(value)
                )
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_post_show_on_third_pages(self):
        """Проверяем что созданный пост появился на трех страницах"""
        self.assertIn(
            Post.objects.get(id=1),
            self.response_index_post_show.context["page_obj"]
        )
        self.assertIn(
            Post.objects.get(id=1),
            self.response_group_list_post_show.context["page_obj"]
        )
        self.assertIn(
            Post.objects.get(id=1),
            self.response_profile_post_show.context["page_obj"]
        )

    def test_another_group_list_page_not_show_post(self):
        """Пост, не принадлежащий группе не показывается."""
        self.assertNotIn(
            Post.objects.get(id=1),
            self.response_group_2.context['page_obj']
        )

    def test_cache_index_correct_context(self):
        response = self.unauthorized_user.get(reverse('posts:main'))
        content = response.content
        context = response.context['page_obj']
        self.assertIn(self.post, context)
        post = Post.objects.get(id=self.post.id)
        post.delete()
        second_response = self.unauthorized_user.get(reverse('posts:main'))
        second_content = second_response.content
        self.assertEqual(content, second_content)
        cache.clear()
        second_response = self.unauthorized_user.get(reverse('posts:main'))
        second_content = second_response.content
        self.assertNotEqual(content, second_content)


class PostPaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        object_list = []
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(12):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group
            )
            object_list.append(cls.post)

    def test_first_page_contains_ten_records_index(self):
        """Проверка паджинатора страниц"""
        paginator = [
            self.client.get(reverse('posts:main')),
            self.client.get(
                reverse('posts:group', kwargs={'slug': 'test-slug'})
            ),
            self.client.get(
                reverse('posts:profile', kwargs={'username': 'auth'})
            ),
        ]
        for paginator_id in paginator:
            response = paginator_id
            # Проверка: количество постов на первой странице равно 10.
            self.assertEqual(
                response.context['page_obj'].paginator.page('1')
                .object_list.count(),
                response.context['page_obj'].paginator.per_page
            )
