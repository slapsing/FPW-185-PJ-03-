from ckeditor.widgets import CKEditorWidget
from django import forms

from .models import Post, Reply


class PostForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorWidget())


    class Meta:
        model = Post
        fields = ["title", "category", "body", "published"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Напишите отклик…"}),
        }