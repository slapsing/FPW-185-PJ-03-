from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.db import models
from django.utils import timezone

from board.choices import CATEGORY_CHOICES

User = settings.AUTH_USER_MODEL


class Category(models.Model):
    code = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Post(models.Model):
    author = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name="posts", on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    body = RichTextUploadingField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)

    def excerpt(self, chars=200):
        import re
        text = re.sub('<[^<]+?>', '', self.body)
        return (text[:chars] + '...') if len(text) > chars else text

    def __str__(self):
        return self.title


class Reply(models.Model):
    post = models.ForeignKey(Post, related_name="replies", on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="replies", on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    accepted = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Reply by {self.author} to {self.post}"


class Subscription(models.Model):
    user = models.ForeignKey(User, related_name="subscriptions", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name="subscriptions", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "category")


class Newsletter(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return self.subject


class Notification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications")
    message = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Уведомление для {self.user}: {self.message}"


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.TextField(blank=True)
    reputation = models.IntegerField(default=0)

    def post_count(self):
        return self.user.posts.count()

    def reply_count(self):
        return self.user.replies.count()

    def accepted_replies_count(self):
        """Количество принятых откликов на посты автора"""
        return Reply.objects.filter(post__author=self.user, accepted=True).count()

    def top_categories(self, limit=3):
        """Чаще всего используемые категории"""
        from django.db.models import Count
        return (
            self.user.posts.values("category__title")
            .annotate(total=Count("id"))
            .order_by("-total")[:limit]
        )

    def last_post(self):
        """Последний пост автора"""
        return self.user.posts.order_by("-created_at").first()

    def __str__(self):
        return self.user.username


class NewsletterSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="newsletter_subscription")
    subscribed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {'подписан' if self.subscribed else 'отписан'}"