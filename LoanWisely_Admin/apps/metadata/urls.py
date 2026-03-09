from django.urls import path
from . import views

urlpatterns = [
    path("credit/", views.credit_meta_list, name="credit_meta_list"),
    path("credit/create/", views.credit_meta_create, name="credit_meta_create"),
    path("credit/<int:version_id>/approve/", views.credit_meta_approve, name="credit_meta_approve"),
    path("financial/", views.financial_meta_list, name="financial_meta_list"),
    path("financial/create/", views.financial_meta_create, name="financial_meta_create"),
    path("financial/<int:version_id>/approve/", views.financial_meta_approve, name="financial_meta_approve"),
]
