from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class StaticUrlTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_404(self):
        """Тест на ошибку 404"""
        response = self.guest_client.get('/page_doesnt_exist')
        self.assertEqual(response.status_code, 404)

    def test_page_404_has_correct_template(self):
        """Страница 404 имеет корректный шаблон"""
        response = self.guest_client.get("/page_doesnt_exist")
        self.assertTemplateUsed(response, "core/404.html")


class TestUrls(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            description="Тестовое описание",
            slug="test_slug"
        )
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )
        cls.not_author_user = (
            User.objects.create_user(username='NotAuthor'))

    def setUp(self):
        self.guest_client = Client()  # Не авторизованный юзер
        # Автор поста, авторизован
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_reverse(self):
        """Проверка reverse"""
        reverse_and_urls = {
            reverse("posts:index"): "/",
            reverse("posts:group_list",
                    kwargs={"slug": self.group.slug}):
                        f"/group/{self.group.slug}/",
            reverse(
                "posts:profile",
                kwargs={"username": self.user}):
                    f"/profile/{self.user}/",
            reverse(
                "posts:post_detail",
                kwargs={"post_id": self.post.pk}):
                    f"/posts/{self.post.pk}/",
            reverse(
                "posts:post_edit",
                kwargs={"post_id": self.post.pk}):
                    f"/posts/{self.post.pk}/edit/",
            reverse("posts:post_create"):
                    "/create/",
            reverse("posts:follow_index"): "/follow/"
        }
        for reversed_name, address in reverse_and_urls.items():
            with self.subTest(address=address):
                self.assertEqual(reversed_name, address)

    def test_access_urls(self):
        """Проверка доступности страниц"""
        data = (
            reverse("posts:index"),
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group.slug}),
            reverse(
                "posts:profile",
                kwargs={"username": self.user}),
            reverse(
                "posts:post_detail",
                kwargs={"post_id": self.post.pk}),
            reverse("posts:post_create"),
            reverse(
                "posts:post_edit",
                kwargs={"post_id": self.post.pk}),
            reverse(
                "posts:follow_index"
            )
        )
        for address in data:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_post_create_for_not_auth_user(self):
        """Страница post_create недоступна
         не авторизированному пользователю"""
        response = self.guest_client.get(
            reverse("posts:post_create"))
        self.assertNotEqual(response.status_code, 200)

    def test_post_edit_for_no_author(self):
        """Страница post_edit не доступна не автору"""
        self.authorized_client.force_login(self.not_author_user)
        response = self.authorized_client.get(
            reverse(
                "posts:post_edit", kwargs={"post_id": self.post.pk})
        )
        self.assertNotEqual(response.status_code, 200)

    def test_templates_names(self):
        """Проверка возвращаемых шаблонов"""
        data = {reverse("posts:index"): "posts/index.html",
                reverse(
                    "posts:group_list",
                    kwargs={"slug": self.group.slug}):
                        "posts/group_list.html",
                reverse(
                    "posts:profile",
                    kwargs={"username": self.user}):
                        "posts/profile.html",
                reverse(
                    "posts:post_detail",
                    kwargs={"post_id": self.post.pk}):
                        "posts/post_detail.html",
                reverse(
                    "posts:post_edit",
                    kwargs={"post_id": self.post.pk}):
                        "posts/create_post.html",
                reverse("posts:post_create"):
                    "posts/create_post.html",
                reverse("posts:follow_index"):
                    "posts/follow.html"
                }

        for address, template in data.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_not_author_redirect_from_post_edit(self):
        """Проверка редиректа не автора поста со страницы post_edit"""
        self.authorized_client.force_login(self.not_author_user)
        response = self.authorized_client.get(
            reverse("posts:post_edit",
                    kwargs={"post_id": self.post.pk}))
        self.assertRedirects(
            response, reverse("posts:post_detail",
                              kwargs={"post_id": self.post.pk}))