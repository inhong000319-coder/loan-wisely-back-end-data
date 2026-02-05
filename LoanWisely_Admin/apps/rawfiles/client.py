import requests
from django.conf import settings


def _auth_header(request):
    header_name = getattr(settings, "JWT_HEADER_NAME", "Authorization")
    cookie_name = getattr(settings, "JWT_COOKIE_NAME", "admin_jwt")

    auth_header = request.headers.get(header_name, "")
    if auth_header:
        return auth_header

    token = request.COOKIES.get(cookie_name)
    if token:
        return f"Bearer {token}"

    return ""


def _headers(request):
    return {
        "Authorization": _auth_header(request),
        "X-Trace-Id": getattr(request, "trace_id", ""),
        "X-Source": "django-admin",
    }


def list_raw_files(request, params=None):
    url = f"{settings.SPRING_BASE_URL}/api/admin/raw-files"
    resp = requests.get(url, headers=_headers(request), params=params, timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return resp.json()


def upload_raw_file(request, files):
    url = f"{settings.SPRING_BASE_URL}/api/admin/raw-files"
    resp = requests.post(url, headers=_headers(request), files=files, timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return resp.json()
