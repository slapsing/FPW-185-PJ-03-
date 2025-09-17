from allauth.account.views import ConfirmEmailView
from allauth.account.views import EmailVerificationSentView as AllauthEmailVerificationSentView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

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
