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


def list_policies(request, params=None):
    url = f"{settings.SPRING_BASE_URL}/api/admin/policies"
    resp = requests.get(url, headers=_headers(request), params=params, timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return resp.json()


def get_policy(request, policy_id):
    url = f"{settings.SPRING_BASE_URL}/api/admin/policies/{policy_id}"
    resp = requests.get(url, headers=_headers(request), timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return resp.json()


def create_policy(request, payload):
    url = f"{settings.SPRING_BASE_URL}/api/admin/policies"
    resp = requests.post(url, headers=_headers(request), json=payload, timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return resp.json()


def update_policy(request, policy_id, payload):
    url = f"{settings.SPRING_BASE_URL}/api/admin/policies/{policy_id}"
    resp = requests.put(url, headers=_headers(request), json=payload, timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return resp.json()


def approve_policy(request, policy_id):
    url = f"{settings.SPRING_BASE_URL}/api/admin/policies/{policy_id}/approve"
    resp = requests.post(url, headers=_headers(request), timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return resp.json()


def deploy_policy(request, policy_id):
    url = f"{settings.SPRING_BASE_URL}/api/admin/policies/{policy_id}/deploy"
    resp = requests.post(url, headers=_headers(request), timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return resp.json()
