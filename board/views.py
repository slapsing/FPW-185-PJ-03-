from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.views.generic.edit import FormMixin
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from config import settings
from .forms import PostForm, ReplyForm
from .models import Post, Reply, Category, Subscription, Notification, Newsletter
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostCreateSerializer,
    ReplySerializer, CategorySerializer, SubscriptionSerializer
)


def index(request):
    posts_qs = Post.objects.filter(published=True).order_by('-created_at')
    paginator = Paginator(posts_qs, 10)

    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('board/post_list_ajax.html', {'posts': page_obj}, request=request)
        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next(),
            'page': page_obj.number,
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        })

    return render(request, 'index.html', {'posts': page_obj})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "board/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "redirect_url": reverse_lazy("post_detail", kwargs={"pk": self.object.pk})
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": False,
                "errors": form.errors.as_json()
            })
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("post_detail", kwargs={"pk": self.object.pk})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "board/post_form.html"

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def get_success_url(self):
        return reverse_lazy("post_detail", kwargs={"pk": self.object.pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "board/post_confirm_delete.html"
    success_url = reverse_lazy("index")

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user


class PostListView(ListView):
    model = Post
    template_name = "board/post_list.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(published=True)
    paginate_by = 5

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string('board/post_list_ajax.html', context, request=self.request)
            return JsonResponse({'html': html})
        else:
            return super().render_to_response(context, **response_kwargs)


class PostDetailView(FormMixin, DetailView):
    model = Post
    template_name = "board/post_detail.html"
    context_object_name = "post"
    form_class = ReplyForm

    def get_success_url(self):
        return reverse("post_detail", kwargs={"pk": self.object.pk})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            if self.object.author == request.user:
                return HttpResponseForbidden("Вы не можете откликаться на свой пост.")

            reply = form.save(commit=False)
            reply.author = request.user
            reply.post = self.object
            reply.save()

            Notification.objects.create(
                user=self.object.author,
                message=f"{request.user.username} оставил отклик на ваш пост '{self.object.title}'",
                url=reverse("post_detail", kwargs={"pk": self.object.pk})
            )

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                replies_html = render_to_string(
                    "board/_reply_list.html", {"post": self.object}, request=request
                )
                return JsonResponse({"html": replies_html})

            return redirect(self.get_success_url())
        return self.form_invalid(form)


@login_required
def accept_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    if reply.post.author != request.user:
        return HttpResponseForbidden("Вы не можете принимать этот отклик.")

    reply.accepted = True
    reply.save()

    Notification.objects.create(
        user=reply.author,
        message=f"Ваш отклик на пост '{reply.post.title}' был принят",
        url=reverse("post_detail", kwargs={"pk": reply.post.pk})
    )

    return redirect("post_detail", pk=reply.post.pk)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(published=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ("list",):
            return PostListSerializer
        if self.action in ("retrieve",):
            return PostDetailSerializer
        return PostCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def reply(self, request, pk=None):
        post = self.get_object()
        serializer = ReplySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReplyViewSet(viewsets.ModelViewSet):
    queryset = Reply.objects.filter(deleted=False)
    serializer_class = ReplySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def accept(self, request, pk=None):
        reply = self.get_object()
        post = reply.post
        if post.author != request.user:
            return Response({"detail": "Not allowed"}, status=403)
        reply.accepted = True
        reply.save()
        return Response({"status": "accepted"})


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@login_required
def my_replies_view(request):
    posts = Post.objects.filter(author=request.user)

    post_id = request.GET.get("post")
    if post_id:
        replies = Reply.objects.filter(post_id=post_id, post__author=request.user, deleted=False)
    else:
        replies = Reply.objects.filter(post__author=request.user, deleted=False)

    # Сортировка по количеству откликов на пост
    order = request.GET.get("order", "desc")
    replies = replies.annotate(num_post_replies=Count("post__replies"))

    if order == "asc":
        replies = replies.order_by("num_post_replies", "-created_at")
    else:
        replies = replies.order_by("-num_post_replies", "-created_at")

    return render(request, "board/my_replies.html", {"posts": posts, "replies": replies})


@login_required
def delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id, post__author=request.user)
    reply.deleted = True
    reply.save()
    return redirect('my_replies')


class PostRankingView(ListView):
    model = Post
    template_name = "board/post_ranking.html"
    context_object_name = "posts"

    def get_queryset(self):
        return Post.objects.filter(published=True).annotate(
            num_replies=Count("replies")
        ).order_by("-num_replies")


@login_required
def my_posts_view(request):
    posts = Post.objects.filter(author=request.user).order_by("-created_at")
    return render(request, "board/my_posts.html", {"posts": posts})


@login_required
def notifications_view(request):
    notifications = request.user.notifications.all()
    return render(request, "board/notifications.html", {"notifications": notifications})


@login_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.read = True
    notif.save()
    return redirect("notifications")


@login_required
def send_newsletter(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    newsletter = get_object_or_404(Newsletter, pk=pk)
    users = User.objects.exclude(email="").values_list("email", flat=True)
    messages = [(newsletter.subject, newsletter.body, settings.DEFAULT_FROM_EMAIL, [u]) for u in users]
    send_mass_mail(messages, fail_silently=True)
    newsletter.sent = True
    newsletter.save()
    return redirect("admin:board_newsletter_changelist")
