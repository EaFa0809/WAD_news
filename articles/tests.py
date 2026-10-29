from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Comment

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

class CommentTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.user = User.objects.create_user(
            username="commentuser",
            password="testpass123",
        )

        cls.article = Article.objects.create(
            title="Article for comments",
            body="This article will receive comments.",
            author=cls.user,
        )

    def test_comment_creation(self):
        comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            comment="Great article!",
        )

        self.assertEqual(comment.comment, "Great article!")
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.article, self.article)

    def test_comment_post_authenticated(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "article_detail",
                args=[self.article.pk],
            ),
            {
                "comment": "This is a test comment.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 1)

        comment = Comment.objects.first()

        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.article, self.article)

    def test_comment_requires_login(self):
        response = self.client.post(
            reverse(
                "article_detail",
                args=[self.article.pk],
            ),
            {
                "comment": "Anonymous comment",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_display(self):
        Comment.objects.create(
            article=self.article,
            author=self.user,
            comment="Visible comment",
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "article_detail",
                args=[self.article.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "Visible comment",
        )