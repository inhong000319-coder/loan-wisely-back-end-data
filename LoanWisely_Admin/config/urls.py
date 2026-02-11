from django.urls import path, include
from django.shortcuts import redirect


def root_redirect(request):
    return redirect("/management/policies/")


urlpatterns = [
    path("", root_redirect),
    path("internal/", include("apps.internal.urls")),
    path("management/auth/", include("apps.auth.urls")),
    path("management/policies/", include("apps.policies.urls")),
    path("management/metadata/", include("apps.metadata.urls")),
    path("management/approvals/", include("apps.approvals.urls")),
    path("management/audits/", include("apps.audits.urls")),
    path("management/recommendations/", include("apps.recommendations.urls")),
    path("management/raw-files/", include("apps.rawfiles.urls")),
]
