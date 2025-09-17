from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin
# from modeltranslation.admin import TranslationAdmin

from .models import Category, Post, Reply, Subscription, Newsletter


class PostAdminForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Post
        fields = "__all__"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ("title", "author", "category", "created_at")
    search_fields = ("title", "body")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("code", "title")


admin.site.register(Reply)
admin.site.register(Subscription)
admin.site.register(Newsletter)
