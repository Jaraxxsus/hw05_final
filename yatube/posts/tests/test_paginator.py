import math

from django.conf import settings
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PaginatorTestView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.COUNT_POSTS: int = 21  # К-во постов
        cls.user = User.objects.create_user(username='test_username')
        cls.group = Group.objects.create(
            title=("Заголовок для тестовой группы"),
            slug="test_slug",
            description="Тестовое описание")
        cls.posts = Post.objects.bulk_create([Post(
            author=cls.user,
            text=f"Тестовый пост {post}",
            group=cls.group) for post in range(cls.COUNT_POSTS)
        ])
        cls.count_pages = math.ceil(cls.COUNT_POSTS / settings.POST_PER_PAGE)
        #  Вычитаемое для формулы нахождения остатка постов на странице
        cls.SUBTRACTABLE_PAGE: int = 1
        cache.clear()

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def test_paginator(self):
        """Проверка работы паджинатора"""
        reverse_names = (
            reverse("posts:index"),
            reverse("posts:group_list",
                    kwargs={"slug": self.group.slug}),
            reverse("posts:profile",
                    kwargs={"username": self.user})
        )

        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    len(response.context["page_obj"]), settings.POST_PER_PAGE)
                response = self.client.get(
                    reverse_name + f"?page={self.count_pages}")

                self.assertEqual(
                    len(response.context["page_obj"]),
                    self.COUNT_POSTS - (
                            self.count_pages - self.SUBTRACTABLE_PAGE)
                    * settings.POST_PER_PAGE)
