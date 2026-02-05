from django.urls import path
from . import views

urlpatterns = [
    path("credit/", views.credit_meta_list, name="credit_meta_list"),
    path("financial/", views.financial_meta_list, name="financial_meta_list"),
]
