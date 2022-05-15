from django.contrib.auth import get_user_model
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
        cls.follow = Follow.objects.create(
            user=cls.follower_user,
            author=cls.following_user
        )

    def setUp(self):
        self.follower_client = Client()
        self.not_follower = Client()
        self.not_follower.force_login(self.user)
        self.follower_client.force_login(self.follower_user)

    def test_follow(self):
        """Тест функционала подписки"""
        self.follower_client.get(reverse(
            "posts:profile_follow", kwargs={"username":
                                            self.following_user}))
        self.assertTrue(Follow.objects.filter(
            user=self.follower_user,
            author=self.following_user
        ).exists())

    def test_unfollow(self):
        """Текст функционала отписки """
        self.follower_client.get(reverse("posts:profile_unfollow",
                                         kwargs={"username": self.following_user}))
        self.assertFalse(
            Follow.objects.filter(
                user=self.follower_user,
                author=self.following_user
            ).exists())

    def test_subscription_page(self):
        """появление записи в ленте"""
        response = self.follower_client.get(reverse("posts:follow_index"))
        self.assertIn(self.post, response.context["page_obj"])
        # Новая запись не появляется в ленте не подписчика
        response = self.not_follower.get(
            reverse("posts:follow_index"))
        self.assertNotContains(response, self.post)
