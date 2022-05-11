from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreateModel

User = get_user_model()


class Post(CreateModel):
    text = models.TextField(verbose_name='Текст поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Группа',
        related_name='posts'
    )
    image = models.ImageField(
        "Картинка",
        upload_to="posts/",
        blank=True
    )

    class Meta:
        ordering = ('-created', )
        verbose_name_plural = 'Список постов'
        verbose_name = 'Пост'

    def __str__(self):
        return str(self.text[:15])


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=30)
    description = models.TextField()

    def __str__(self):
        return self.title


class Comment(CreateModel):
    post = models.ForeignKey(
        Post,
        related_name="comments",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name="comments",
        on_delete=models.CASCADE,
    )
    text = models.TextField(verbose_name='Текст комментария')

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name="follower",
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name="following",
        on_delete=models.CASCADE

    )
