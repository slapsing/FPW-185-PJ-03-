from django.urls import path

from .views import (
    profile_view,
    edit_profile,
    EmailVerificationSentView,
    EmailConfirmView,
)

urlpatterns = [
    path("account-email-verification-sent/", EmailVerificationSentView.as_view(),
         name="account_email_verification_sent"),

    path("account-confirm-email/<str:key>/", EmailConfirmView.as_view(),
         name="account_confirm_email"),

    path("profile/", profile_view, name="profile"),
    path("profile/edit/", edit_profile, name="account_edit_profile"),
]
