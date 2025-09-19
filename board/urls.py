from django.urls import path

from . import views
from .views import (
    my_replies_view, delete_reply,
    PostListView, PostDetailView,
    PostCreateView, PostUpdateView,
    PostDeleteView, PostRankingView
)

urlpatterns = [
    path('', views.index, name='index'),

    path("my-posts/", views.my_posts_view, name="my_posts"),
    path('my-replies/', my_replies_view, name='my_replies'),
    path('reply/<int:reply_id>/delete/', delete_reply, name='reply_delete'),
    path("replies/<int:pk>/accept/", views.accept_reply, name="reply_accept"),

    path("posts/", PostListView.as_view(), name="post_list"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("posts/create/", PostCreateView.as_view(), name="post_create"),
    path("posts/<int:pk>/edit/", PostUpdateView.as_view(), name="post_update"),
    path("posts/<int:pk>/delete/", PostDeleteView.as_view(), name="post_delete"),



    path("ranking/", PostRankingView.as_view(), name="post_ranking"),

    path("notifications/", views.notifications_view, name="notifications"),
    path("notifications/<int:pk>/read/", views.mark_notification_read, name="notification_read"),



]
