import requests
from django.conf import settings
from apps.common.api import unwrap_api_response


def _auth_header(request):
    header_name = getattr(settings, "JWT_HEADER_NAME", "Authorization")
    cookie_name = getattr(settings, "JWT_COOKIE_NAME", "admin_jwt")

    auth_header = request.headers.get(header_name, "")
    if auth_header:
        return auth_header

    token = request.COOKIES.get(cookie_name)
    if token:
        return f"Bearer {token}"

    fallback = getattr(settings, "SPRING_ADMIN_TOKEN", "")
    if fallback:
        return f"Bearer {fallback}"

    return ""


def _headers(request):
    return {
        "Authorization": _auth_header(request),
        "X-Trace-Id": getattr(request, "trace_id", ""),
        "X-Source": "django-admin",
    }


def list_credit_meta(request, params=None):
    url = f"{settings.SPRING_BASE_URL}/api/admin/metadata/credit-dictionary/versions"
    resp = requests.get(url, headers=_headers(request), params=params, timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return unwrap_api_response(resp)


def list_financial_meta(request, params=None):
    url = f"{settings.SPRING_BASE_URL}/api/admin/metadata/financial-meta/versions"
    resp = requests.get(url, headers=_headers(request), params=params, timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return unwrap_api_response(resp)


def create_credit_meta_version(request, payload):
    url = f"{settings.SPRING_BASE_URL}/api/admin/metadata/credit-dictionary/versions"
    resp = requests.post(url, headers=_headers(request), json=payload, timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return unwrap_api_response(resp)


def approve_credit_meta_version(request, version_id):
    url = f"{settings.SPRING_BASE_URL}/api/admin/metadata/credit-dictionary/versions/{version_id}/approve"
    resp = requests.post(url, headers=_headers(request), timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return unwrap_api_response(resp)


def create_financial_meta_version(request, payload):
    url = f"{settings.SPRING_BASE_URL}/api/admin/metadata/financial-meta/versions"
    resp = requests.post(url, headers=_headers(request), json=payload, timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return unwrap_api_response(resp)


def approve_financial_meta_version(request, version_id):
    url = f"{settings.SPRING_BASE_URL}/api/admin/metadata/financial-meta/versions/{version_id}/approve"
    resp = requests.post(url, headers=_headers(request), timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return unwrap_api_response(resp)
