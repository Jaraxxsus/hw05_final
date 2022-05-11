from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class TestCache(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def setUp(self):
        self.guest_client = Client()  # Не авторизованный юзер
        cache.clear()

    def test_post_in_cache(self):
        """При удалении поста, он остается в кеше"""
        response_before_deleting_post = self.guest_client.get(
            reverse("posts:index"))
        post_obj = Post.objects.get(pk=1)
        post_obj.delete()
        response_after_deleting_post = self.guest_client.get(
            reverse("posts:index"))
        self.assertEqual(
            response_before_deleting_post.content,
            response_after_deleting_post.content)
        cache.clear()
        response_after_clear_cache = self.guest_client.get(
            reverse("posts:index"))
        self.assertNotEqual(
            response_after_clear_cache.content,
            response_before_deleting_post.content
        )

