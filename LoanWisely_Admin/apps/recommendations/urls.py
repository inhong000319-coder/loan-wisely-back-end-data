from django.urls import path
from . import views

urlpatterns = [
    path("", views.recommendation_detail),
    path("event-logs", views.event_logs),
    path("reject-logs", views.reject_logs),
    path("exclusion-reasons", views.exclusion_reasons),
]
