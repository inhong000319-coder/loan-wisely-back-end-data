from django.urls import path
from . import views

urlpatterns = [
    path("", views.approval_list, name="approval_list"),
    path("<str:target_id>/", views.approval_detail, name="approval_detail"),
]
