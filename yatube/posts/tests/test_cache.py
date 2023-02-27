from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from ..models import Post, Group

User = get_user_model()

"""
- создал пост
- загрузил главную, сохранил респонс
- удалил пост
- загрузил главную, сохранил респонс
- проверил, что response.content у обоих одинаков
- вручную очистил кэш через cache.clear()
- загрузил главную, сохранил респонс
- проверил, что контент изменился
"""


class CachePagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='NoName')

        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовое описание поста',
            group=self.group
        )

    def test_cache_index_page(self):
        response_before_del_post = self.client.get(reverse('posts:index'))
        self.post.delete()
        response_after_del_post = self.client.get(reverse('posts:index'))
        self.assertEqual(response_before_del_post.content,
                         response_after_del_post.content)
        cache.clear()
        response_after_cache_clear = self.client.get(reverse('posts:index'))
        self.assertNotEqual(response_after_del_post.content,
                            response_after_cache_clear.content)
