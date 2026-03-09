from django.urls import path
from . import views

urlpatterns = [
    path("", views.policy_list, name="policy_list"),
    path("new", views.policy_create, name="policy_create"),
    path("<str:policy_id>/", views.policy_detail, name="policy_detail"),
    path("<str:policy_id>/approve", views.policy_approve, name="policy_approve"),
    path("<str:policy_id>/deploy", views.policy_deploy, name="policy_deploy"),
    path("<str:policy_id>/deploy-history", views.policy_deploy_history, name="policy_deploy_history"),
]
