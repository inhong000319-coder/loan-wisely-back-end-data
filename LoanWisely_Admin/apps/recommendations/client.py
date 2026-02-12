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


def get_recommendation_detail(request, recommendation_id):
    url = f"{settings.SPRING_BASE_URL}/api/admin/recommendations/{recommendation_id}"
    resp = requests.get(url, headers=_headers(request), timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return unwrap_api_response(resp)


def get_event_logs(request, product_id):
    url = f"{settings.SPRING_BASE_URL}/api/admin/recommendations/event-logs"
    resp = requests.get(
        url,
        headers=_headers(request),
        params={"productId": product_id},
        timeout=settings.SPRING_TIMEOUT_SECS,
    )
    resp.raise_for_status()
    return unwrap_api_response(resp)


def get_reject_logs(request, request_id):
    url = f"{settings.SPRING_BASE_URL}/api/admin/recommendations/reject-logs"
    resp = requests.get(
        url,
        headers=_headers(request),
        params={"requestId": request_id},
        timeout=settings.SPRING_TIMEOUT_SECS,
    )
    resp.raise_for_status()
    return unwrap_api_response(resp)


def get_exclusion_reasons(request, result_id):
    url = f"{settings.SPRING_BASE_URL}/api/admin/recommendations/exclusion-reasons"
    resp = requests.get(
        url,
        headers=_headers(request),
        params={"resultId": result_id},
        timeout=settings.SPRING_TIMEOUT_SECS,
    )
    resp.raise_for_status()
    return unwrap_api_response(resp)
