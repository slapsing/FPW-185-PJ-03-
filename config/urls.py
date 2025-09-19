from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework import routers

from board import views

router = routers.DefaultRouter()
router.register("categories", views.CategoryViewSet)
router.register("posts", views.PostViewSet, basename="post")
router.register("replies", views.ReplyViewSet)

urlpatterns = [
    # ==== API ====
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    path("auth/", include("sign.urls")),

    path("", include("board.urls")),
    path("admin/", admin.site.urls),

    path('ckeditor/', include('ckeditor_uploader.urls')),
]

# Allauth
urlpatterns += [
    path("accounts/", include("allauth.urls")),
    path("account/", include("allauth.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
