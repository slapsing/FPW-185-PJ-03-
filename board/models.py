from ckeditor.fields import RichTextField
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
    body = RichTextField()
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
