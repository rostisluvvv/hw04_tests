from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus


User = get_user_model()


class UsersURLTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='auth')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def auth_or_guest_user(self, url_address):
        if 'password_change' in url_address:
            return self.authorized_client.get(url_address)
        else:
            return self.guest_client.get(url_address)

    def test_url_status(self):
        pages: tuple = (
            '/auth/signup/',
            '/auth/logout/',
            '/auth/password_change/',
            '/auth/password_change/done',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/done/'
        )

        for page in pages:
            response = self.auth_or_guest_user(page)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        templates_url_names: dict = {
            'users/signup.html': '/auth/signup/',
            'users/logged_out.html': '/auth/logout/',
            'users/password_change_form.html': '/auth/password_change/',
            'users/password_change_done.html': '/auth/password_change/done',
            'users/password_reset_form.html': '/auth/password_reset/',
            'users/password_reset_done.html': '/auth/password_reset/done/',
            'users/password_reset_complete.html': '/auth/reset/done/',
        }

        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.auth_or_guest_user(address)
                self.assertTemplateUsed(response, template)
