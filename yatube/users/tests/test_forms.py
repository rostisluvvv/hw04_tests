from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class UserCreationForm(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='Two_User_NoName')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_user(self):
        count_user = User.objects.count()

        form_data = {
            'first_name': self.user.username,
            'last_name': 'test_last_name',
            'username': 'test_user_name',
            'email': 'test_email@email.com',
            'password1': 'test_37AjNpAFpV4Eqt_password',
            'password2': 'test_37AjNpAFpV4Eqt_password',
        }

        response = self.authorized_client.post(
            reverse('users:signup'), data=form_data)
        self.assertEqual(User.objects.count(), count_user + 1)
        self.assertRedirects(response, reverse('posts:index'))
