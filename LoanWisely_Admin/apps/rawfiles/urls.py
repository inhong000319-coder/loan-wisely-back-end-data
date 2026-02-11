from django.urls import path
from . import views

urlpatterns = [
    path("", views.rawfile_list, name="rawfile_list"),
    path("upload", views.rawfile_upload, name="rawfile_upload"),
    path("<int:upload_id>/validate", views.rawfile_validate, name="rawfile_validate"),
    path("<int:upload_id>/ingest", views.rawfile_ingest, name="rawfile_ingest"),
]
