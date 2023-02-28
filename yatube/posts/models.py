from django.db import models
from django.contrib.auth import get_user_model

from core.models import PubDateModels

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(max_length=400)

    def __str__(self):
        return self.title


class Post(PubDateModels):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста',
        max_length=200
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField('image', upload_to='posts/', blank=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(PubDateModels):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField('Comment of post',
                            help_text='Enter a comment to the post')


class Follow(models.Model):
    # чел который подписывается
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE
    )
    # чел на которого подписываюсь
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        null=True
    )
