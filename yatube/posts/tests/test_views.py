import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.conf import settings

from ..models import Post, Group, Comment, Follow
from ..forms import PostForm


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

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
            description='Тестовое описание группы'
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовое описание поста',
            group=self.group,
            image=uploaded
        )
        self.form_fields: dict = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

    def check_form_fields(self, response, value, expected):
        form_field = response.context.get('form').fields.get(value)
        self.assertIsInstance(form_field, expected)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names: dict = {
            reverse('posts:index'): 'posts/index.html',

            reverse('posts:group_list', kwargs={'slug': 'test-slug'}): (
                'posts/group_list.html'
            ),

            reverse('posts:profile', kwargs={'username': self.user}): (
                'posts/profile.html'
            ),

            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}): (
                'posts/post_detail.html'
            ),

            reverse('posts:post_create'): 'posts/create_post.html',

            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}): (
                'posts/create_post.html'
            )
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_added_correctly(self):
        response_index = self.authorized_client.get(reverse('posts:index'))

        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}))

        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))

        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']

        reverse_name_context: dict = {
            response_index: index,
            response_group: group,
            response_profile: profile
        }
        for response_name, context in reverse_name_context.items():
            with self.subTest(response_name=response_name):

                self.assertIn(self.post, context)

    def test_index_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.context.get('page_obj')[0].text,
                         'Тестовое описание поста')

        self.assertEqual(response.context.get('page_obj')[0].author,
                         self.user)

        self.assertEqual(response.context.get('page_obj')[0].image,
                         self.post.image)

    def test_group_posts_context(self):
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        first_object = response.context['group']

        group_posts: dict = {
            first_object.title: 'Тестовая группа',
            first_object.slug: 'test-slug',
            first_object.description: 'Тестовое описание группы',
        }

        for field, test_value in group_posts.items():
            with self.subTest(field=field):
                self.assertEqual(field, test_value)

        self.assertEqual(
            response.context.get('page_obj')[0].group, self.group)

        self.assertEqual(response.context.get('page_obj')[0].image,
                         self.post.image)

    def test_profile_context(self):
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(
            response.context.get('page_obj')[0].author, self.user)

        self.assertEqual(response.context.get('page_obj')[0].image,
                         self.post.image)

    def test_post_detail_context(self):
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(
            response.context.get('posts_detail').id, self.post.pk
        )
        self.assertEqual(response.context.get('posts_detail').image,
                         self.post.image)

    def test_post_create_form(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                self.check_form_fields(response, value, expected)
        form = response.context['form']
        self.assertIsInstance(form, PostForm)

    def test_post_edit_form(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                self.check_form_fields(response, value, expected)
        is_edit = response.context['is_edit']
        self.assertTrue(is_edit)
        self.assertIsInstance(is_edit, bool)
        form = response.context['form']
        self.assertIsInstance(form, PostForm)

    def test_comment_added_only_auth_authorized_client(self):
        count_comment = Comment.objects.count()
        form_data = {
            'text': 'test comment 2'
        }
        response = self.client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.pk}),
            data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), count_comment)


class PaginatorViewTest(TestCase):
    TEST_OF_POST: int = 13
    COUNT_POST_SECOND_PAGE: int = TEST_OF_POST - settings.COUNT_POSTS

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='test group',
            slug='test-slug'
        )
        blank_post: list = []
        for i in range(self.TEST_OF_POST):
            blank_post.append(Post(text=f'test text {i}',
                                   group=self.group,
                                   author=self.user))
        Post.objects.bulk_create(blank_post)

    def test_index_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']),
                         settings.COUNT_POSTS)

    def test_index_second_page_contains_three_records(self):
        params = {'page': 2}
        response = self.client.get(reverse('posts:index'), params)
        self.assertEqual(len(response.context['page_obj']),
                         self.COUNT_POST_SECOND_PAGE)

    def test_group_first_page_contains_ten_records_group(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(len(response.context['page_obj']),
                         settings.COUNT_POSTS)

    def test_group_second_page_contains_three_records(self):
        params = {'page': 2}
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}), params)
        self.assertEqual(len(response.context['page_obj']),
                         self.COUNT_POST_SECOND_PAGE)

    def test_profile_first_page_contains_ten_records_group(self):
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username}))
        self.assertEqual(len(response.context['page_obj']),
                         settings.COUNT_POSTS)

    def test_profile_second_page_contains_three_records(self):
        params = {'page': 2}
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}), params)
        self.assertEqual(len(response.context['page_obj']),
                         self.COUNT_POST_SECOND_PAGE)


class FollowTests(TestCase):
    COUNT_POST = 0

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.user_following = User.objects.create_user(
            username='user_following'
        )
        self.user_follower = User.objects.create_user(
            username='user_follower'
        )
        self.client_following = Client()
        self.client_follower = Client()
        self.client_following.force_login(self.user_following)
        self.client_follower.force_login(self.user_follower)

        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        self.post = Post.objects.create(
            author=self.user_following,
            text='Тестовое описание поста',
            group=self.group
        )

    def test_authorized_client_can_follow(self):
        follow_count = Follow.objects.count()
        self.client_follower.post(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_following.username}))
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_authorized_client_can_unfollow(self):
        follow_count = Follow.objects.count()
        self.client_follower.post(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user_following.username}))
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_new_post_appears_in_subscribers(self):

        Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        response = self.client_follower.post(reverse('posts:follow_index'))
        self.assertEqual(response.context['page_obj'][0],
                         self.post)

        response = self.client_following.post(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']),
                         self.COUNT_POST)
