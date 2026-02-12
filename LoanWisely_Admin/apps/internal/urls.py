from django.urls import path
from . import views

urlpatterns = [
    path("health", views.health),
    path("admin/metadata/active", views.active_metadata),
    path("admin/financial-meta/versions", views.create_financial_meta_version),
    path("admin/financial-meta/versions/<int:version_id>/approve", views.approve_financial_meta_version),
]
