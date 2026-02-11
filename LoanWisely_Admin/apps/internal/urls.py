from django.urls import path
from . import views

urlpatterns = [
    path("health", views.health),
    path("admin/metadata/active", views.active_metadata),
]
