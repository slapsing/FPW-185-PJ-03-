from django.urls import path

from . import views
from .views import (
    profile_view,
    edit_profile,
    EmailVerificationSentView,
    EmailConfirmView, author_card_view,
)

urlpatterns = [
    path("account-email-verification-sent/", EmailVerificationSentView.as_view(),
         name="account_email_verification_sent"),

    path("account-confirm-email/<str:key>/", EmailConfirmView.as_view(),
         name="account_confirm_email"),

    path("profile/", profile_view, name="profile"),
    path("profile/edit/", edit_profile, name="account_edit_profile"),

    path("profile/<int:user_id>/", author_card_view, name="author_card"),

]
