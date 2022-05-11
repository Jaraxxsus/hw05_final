from django.contrib.auth import get_user_model
from django.core.cache import cache

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class TestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug"
        )
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            text="Тестовый пост",
            author=cls.user,
            group=cls.group,
        )

        cls.EXPECTED_COUNT_POSTS: int = 1
        cache.clear()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()


    def test_pages_correct_context(self):
        """Шаблоны index, group_list, profile
        сформированы с правильным контекстом"""
        urls = (
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={"slug": self.group.slug}),
            reverse("posts:profile",
                    kwargs={'username': self.user}),
        )
        for reverse_name in urls:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                if reverse_name == reverse('posts:group_list',
                                           kwargs={"slug": self.group.slug}):
                    self.assertEqual(self.group, response.context["group"])
                if reverse_name == reverse("posts:profile",
                                           kwargs={'username': self.user}):
                    self.assertEqual(self.user, response.context["author"])

                self.assertIn(self.post,
                              response.context["page_obj"])

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован
         с правильным контекстом"""

        response = self.authorized_client.get(
            reverse("posts:post_detail",
                    kwargs={"post_id": self.post.pk})
        )
        self.assertEqual(response.context["post"],
                         self.post)
        self.assertEqual(response.context["count_posts"],
                         self.EXPECTED_COUNT_POSTS)

    def test_create_post(self):
        """Неавторизованный пользователь не может
        оставить комментарий"""
        response = self.guest_client.get(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk})
            )
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next="
            f"{reverse('posts:add_comment', kwargs={'post_id': self.post.pk})}"
        )

    def test_post_with_img_context(self):
        """Проверка картинки в контексте поста"""
        urls = (
            reverse("posts:post_detail",
                    kwargs={"post_id": self.post.pk}),
            reverse('posts:group_list',
                    kwargs={"slug": self.group.slug}),
            reverse("posts:profile",
                    kwargs={'username': self.user}),
            reverse("posts:index"),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                if url == reverse("posts:post_detail",
                                  kwargs={"post_id": self.post.pk}):
                    self.assertEqual(self.post.image,
                                     response.context["post"].image)
                else:
                    self.assertEqual(self.post.image,
                                     response.context["page_obj"][0].image)




