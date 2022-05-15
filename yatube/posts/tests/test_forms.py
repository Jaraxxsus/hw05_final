import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user("test_user")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="slug555",
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text="Пост555",
            group=cls.group,
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_form(self):
        """Валидная форма создает запись в Posts."""
        post_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст",
            "group": self.group.id,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data["text"],
                author=self.user,
                group=self.group
            ).exists()
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        # Проверка редиректа
        self.assertRedirects(
            response, reverse("posts:profile",
                              kwargs={"username": self.user}))

    def test_edit_post_form(self):
        """Валидная запись изменяет содержание поста"""
        form_data = {
            "text": "Тестовый текст2",
            "group": self.group.id,
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id":
                                               self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.get(pk=self.post.pk).text, form_data["text"])
        #  Проверка редиректа на страницу просмотра поста
        self.assertRedirects(
            response, reverse("posts:post_detail",
                              kwargs={"post_id": self.post.pk})
        )

    def test_saving_post_by_not_logged_user(self):
        """Проверка, что неавторизованный пользователь
        не может создать пост"""
        post_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст",
            "group": self.group.id,
        }
        response = self.guest_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.count(), post_count
        )
        # Тест редиректа
        self.assertRedirects(response,
                             reverse("users:login")
                             + f"?next={reverse('posts:post_create')}")

    def test_adding_comment(self):
        """Проверка добавления коммента к посту"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Какой-то коммент',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={"post_id": self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        # проверка текста коммента
        self.assertEqual("Какой-то коммент", form_data["text"])
        # комментарий у нужного поста
        response = self.authorized_client.get(reverse(
            "posts:post_detail", kwargs={"post_id": self.post.pk}
        ))
        self.assertIn(Comment.objects.get(text="Какой-то коммент"),
                      response.context["comments"])

    def test_post_with_picture(self):
        """Тестирование картинки поста"""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif"
        )
        form_data = {
            'text': "Какой-то пост",
            "group": self.group.id,
            "image": uploaded,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("posts:profile", kwargs={"username": self.user}))

        self.assertTrue(
            Post.objects.filter(
                text="Какой-то пост",
                group=self.group,
                image="posts/small.gif"
            ).exists()
        )
        # Проверка появления поста с картинкой в БД
        self.assertEqual(posts_count + 1, Post.objects.count())

