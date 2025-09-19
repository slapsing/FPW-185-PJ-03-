from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms

from .models import Post, Reply, Category


class PostForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Post
        fields = ["title", "category", "body", "published"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Введите заголовок объявления",
            }),
            "category": forms.Select(attrs={"class": "form-select"}),
            "published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all().order_by("title")
        self.fields["category"].label = "Категория"
        self.fields["category"].empty_label = "Выберите категорию"


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Напишите отклик…"}),
        }
