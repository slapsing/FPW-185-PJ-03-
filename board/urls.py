from django.urls import path
from . import views
from .management.test_email import test_email

urlpatterns = [
    path('', views.index, name='index'),


]