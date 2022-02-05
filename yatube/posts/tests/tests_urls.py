# posts/tests/tests_url.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models import Post, Group


User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='user_author')
        cls.user_nonauthor = User.objects.create_user(
            username='user_nonauthor'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовая группа',
            group=cls.group
        )

    def setUp(self):
        self.unauthorized_user = Client()
        self.post_author = Client()
        self.post_author.force_login(self.user_author)
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user_nonauthor)

    # ------------Тесты доступности страниц------------

    def test_urls_for_post_author(self):
        """Страницы доступны авторизованному автору."""
        urls = [
            '/',
            '/group/test-slug/',
            '/profile/user_author/',
            f'/posts/{self.post.id}/',
            '/create/',
            f'/posts/{self.post.id}/edit/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.post_author.get(url)
                self.assertEqual(response.reason_phrase, 'OK')

    def test_urls_for_nonauthorized_user(self):
        """Страницы доступны любому пользователю."""
        urls = [
            '/',
            '/group/test-slug/',
            '/profile/user_author/',
            f'/posts/{self.post.id}/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.unauthorized_user.get(url)
                self.assertEqual(response.reason_phrase, 'OK')

    def test_urls_for_authorized_user(self):
        """Страницы доступны авторизованному пользователю."""
        urls = [
            '/',
            '/group/test-slug/',
            '/profile/user_author/',
            f'/posts/{self.post.id}/',
            '/create/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_user.get(url)
                self.assertEqual(response.reason_phrase, 'OK')

    def test_unexisting_page_authorized(self):
        """Несуществующая страница не отображается для авторизованного
        ползователя."""
        response = self.authorized_user.get('/unexisting_page/')
        self.assertEqual(response.reason_phrase, 'Not Found')

    def test_unexisting_page_nonauthorized(self):
        """Несуществующая страница не отображается для любого ползователя."""
        response = self.unauthorized_user.get('/unexisting_page/')
        self.assertEqual(response.reason_phrase, 'Not Found')

    def test_unexisting_page_post_author(self):
        """Несуществующая страница не отображается для авторизованного
        автора."""
        response = self.post_author.get('/unexisting_page/')
        self.assertEqual(response.reason_phrase, 'Not Found')

    # ---Проверяем редиректы для неавторизованного пользователя---

    def test_post_edit_url_redirect_anonymous(self):
        """Страница /posts/<post_id>/edit перенаправляет анонимного
        пользователя."""
        response = self.unauthorized_user.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.reason_phrase, 'Found')

    def test_post_create_url_redirect_anonymous(self):
        """Страница /posts/create/ перенаправляет анонимного пользователя. """
        response = self.unauthorized_user.get('/create/')
        self.assertEqual(response.reason_phrase, 'Found')

    # ------------Проверка вызываемых HTML-шаблонов------------

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/user_author/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.post_author.get(address)
                self.assertTemplateUsed(response, template)
