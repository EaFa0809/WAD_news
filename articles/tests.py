from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Article


class ArticlePermissionTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.user1 = User.objects.create_user(
            username="user1",
            password="testpass123",
        )

        cls.user2 = User.objects.create_user(
            username="user2",
            password="testpass123",
        )

        cls.article = Article.objects.create(
            title="Test Article",
            body="This is a test article.",
            author=cls.user1,
        )

    def test_article_list_requires_login(self):
        response = self.client.get(reverse("article_list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_author_can_edit_article(self):
        self.client.force_login(self.user1)

        response = self.client.get(
            reverse("article_edit", args=[self.article.pk])
        )

        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_edit_article(self):
        self.client.force_login(self.user2)

        response = self.client.get(
            reverse("article_edit", args=[self.article.pk])
        )

        self.assertEqual(response.status_code, 403)

    def test_other_user_cannot_delete_article(self):
        self.client.force_login(self.user2)

        response = self.client.post(
            reverse("article_delete", args=[self.article.pk])
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Article.objects.filter(pk=self.article.pk).exists()
        )

    def test_article_author_assigned_automatically(self):
        self.client.force_login(self.user2)

        response = self.client.post(
            reverse("article_new"),
            {
                "title": "New Article",
                "body": "Article content",
            },
        )

        self.assertEqual(response.status_code, 302)

        article = Article.objects.get(title="New Article")

        self.assertEqual(article.author, self.user2)