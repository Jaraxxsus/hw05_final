from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Post

User = get_user_model()


class TestFollowing(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="test_user")
        cls.follower_user = User.objects.create_user(username='follower')
        cls.following_user = User.objects.create_user(username="following")
        cls.post = Post.objects.create(
            text="Тестовый пост",
            author=cls.following_user,
        )

    def setUp(self):
        self.follower = Client()
        self.following = Client()
        self.not_follower = Client()
        self.not_follower.force_login(self.user)
        self.follower.force_login(self.follower_user)
        self.following.force_login(self.following_user)
        cache.clear()

    def test_follow(self):
        """Тест функционала подписки"""
        follow_count = Follow.objects.count()
        self.follower.get(reverse("posts:profile_follow",
                                  kwargs={"username": self.following_user}))
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_unfollow(self):
        """Текст функционала отписки """
        # Подписываемся, получаем подписку
        self.follower.get(reverse("posts:profile_follow",
                                  kwargs={"username": self.following_user}))
        # Отписываемся, вычитаем подписку, получаем 0
        self.follower.get(reverse("posts:profile_unfollow",
                                  kwargs={"username": self.following_user}))
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_subscription_page(self):
        """появление записи в ленте"""
        Follow.objects.create(user=self.follower_user,
                              author=self.following_user)
        response = self.follower.get(reverse("posts:follow_index"))
        self.assertIn(self.post, response.context["page_obj"])
        # Новая запись не появляется в ленте не подписчика
        response = self.not_follower.get(
            reverse("posts:follow_index"))
        self.assertNotContains(response, self.post)
