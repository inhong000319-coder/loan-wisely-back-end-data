from django.urls import path
from . import views

urlpatterns = [
    path("", views.rawfile_list, name="rawfile_list"),
    path("upload", views.rawfile_upload, name="rawfile_upload"),
]
