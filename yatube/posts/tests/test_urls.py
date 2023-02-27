from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group


User = get_user_model()


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_not_author = User.objects.create_user(username='not_author')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.not_author_client = Client()
        self.not_author_client.force_login(self.user_not_author)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание'
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовое описание поста')

    def test_urls_uses_correct_template(self):
        templates_url_names: dict = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_authorized_client_status_ok(self):
        url_names: tuple = (
            f'/posts/{self.post.id}/edit/',
            '/create/'
        )
        for address in url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_guest_client_status_ok(self):
        url_names: tuple = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.id}/',
        )
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_edit_not_author(self):
        redirect_pages: dict = {
            f'/posts/{self.post.pk}/edit/': f'/posts/{self.post.pk}/'
        }
        for address, redirect_address in redirect_pages.items():
            with self.subTest(address=address):
                response = self.not_author_client.get(address)
                self.assertRedirects(response, redirect_address)

    def test_redirect_guest_client(self):
        redirect_create_url = '/auth/login/?next=/create/'
        redirect_edit_url = f'/auth/login/?next=/posts/{self.post.pk}/edit/'

        pages: dict = {
            '/create/': redirect_create_url,
            f'/posts/{self.post.id}/edit/': redirect_edit_url
        }

        for page, redirect_page in pages.items():
            response = self.guest_client.get(page)
            self.assertRedirects(response, redirect_page)

    def test_unexisting_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
