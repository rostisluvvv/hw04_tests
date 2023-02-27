import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings

from ..models import Post, Group, Comment


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='NoName')

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')

        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовое описание поста',
            group=self.group,
            image=uploaded
        )
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
        post_count = Post.objects.count()
        old_text = self.post.text

        editable_fields = {
            'text': 'редактированный текст поста',
            'group': self.post.group.pk,
            'image': self.post.image
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=editable_fields)
        new_text = editable_fields['text']

        self.assertEqual(Post.objects.count(), post_count)

        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}))

        self.assertNotEqual(old_text, new_text)


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='NoName')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовое описание поста',
            group=self.group
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            text='test comment 1'
        )

    def test_added_comment(self):
        count_comment = Comment.objects.count()
        form_data = {
            'text': 'test comment 2'
        }
        self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.pk}),
            data=form_data)
        self.assertEqual(Comment.objects.count(), count_comment + 1)
