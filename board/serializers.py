from rest_framework import serializers

from .models import Post, Reply, Category, Subscription


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "code", "title")


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    category = CategorySerializer()

    class Meta:
        model = Post
        fields = ("id", "title", "excerpt", "author", "category", "created_at", "published")


class PostDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Post
        fields = ("id", "title", "body", "author", "category", "created_at", "updated_at", "published")


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "title", "body", "category", "published")


class ReplySerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Reply
        fields = ("id", "post", "author", "text", "created_at", "accepted", "deleted")
        read_only_fields = ("author", "created_at", "accepted", "deleted")


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("id","user","category","created_at")
        read_only_fields = ("user","created_at")