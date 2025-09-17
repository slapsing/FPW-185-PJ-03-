from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
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

from .forms import PostForm, ReplyForm
from .models import Post, Reply, Category, Subscription
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostCreateSerializer,
    ReplySerializer, CategorySerializer, SubscriptionSerializer
)


def index(request):
    posts = Post.objects.filter(published=True).order_by('-created_at')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('board/post_list_ajax.html', {'posts': page_obj})
        return JsonResponse({'html': html})

    return render(request, 'index.html', {'posts': page_obj})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "board/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

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
    paginate_by = 10


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
            reply = form.save(commit=False)
            reply.author = request.user
            reply.post = self.object
            reply.save()
            return redirect(self.get_success_url())
        return self.form_invalid(form)


@login_required
def accept_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    if reply.post.author != request.user:
        return HttpResponseForbidden("Вы не можете принимать этот отклик.")
    reply.accepted = True
    reply.save()
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
