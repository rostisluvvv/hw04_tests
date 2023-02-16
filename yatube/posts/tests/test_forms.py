from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from ..models import Post, Group
from django.urls import reverse


User = get_user_model()


class PostCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовое описание поста',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        count_post = Post.objects.count()
        form_data = {
            'text': 'Тестовое описание поста',
            'group': self.post.group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data)

        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}))

        self.assertEqual(Post.objects.count(), count_post + 1)

        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Тестовое описание поста',
                group=self.post.group.pk
            )
        )

    def test_post_edit(self):
        old_text = self.post
        editable_fields = {
            'text': 'редактированный текст поста',
            'group': self.post.group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=editable_fields)
        new_text = editable_fields['text']

        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}))

        self.assertNotEqual(old_text, new_text)
