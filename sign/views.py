from allauth.account.views import ConfirmEmailView
from allauth.account.views import EmailVerificationSentView as AllauthEmailVerificationSentView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from board.models import Post, Reply, Author
from .forms import ProfileEditForm


class CustomConfirmEmailView(ConfirmEmailView):
    template_name = "sign/email_confirmed.html"
    success_url = reverse_lazy("account_login")


@login_required
def profile_view(request):
    return render(request, "sign/profile.html", {
        'user': request.user,
        # 'posts_count': request.user.posts.count(),
        'last_login': request.user.last_login,
    })


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Имя успешно обновлено ✅")
            return redirect("profile")
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, "sign/edit_profile.html", {"form": form})


class EmailVerificationSentView(AllauthEmailVerificationSentView):
    template_name = "sign/email_verification_sent.html"


class EmailConfirmView(TemplateView):
    template_name = "sign/confirm_email.html"


def author_card_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    author_card, created = Author.objects.get_or_create(user=user)

    # Статистика
    posts_count = Post.objects.filter(author=user).count()
    replies_count = Reply.objects.filter(author=user).count()
    accepted_replies = Reply.objects.filter(post__author=user, accepted=True).count()

    # Последний пост
    last_post = Post.objects.filter(author=user).order_by("-created_at").first()

    # Топ категорий
    top_categories = (
        Post.objects.filter(author=user)
        .values("category__title")
        .annotate(cnt=Count("id"))
        .order_by("-cnt")[:5]
    )

    context = {
        "author": user,
        "card": author_card,
        "posts_count": posts_count,
        "replies_count": replies_count,
        "accepted_replies": accepted_replies,
        "last_post": last_post,
        "top_categories": top_categories,
    }
    return render(request, "account/author_card.html", context)
