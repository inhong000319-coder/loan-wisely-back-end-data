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


def get_recommendation_es_search(request, user_id, policy_version, keyword, date_from, date_to, page, size):
    url = f"{settings.SPRING_BASE_URL}/api/admin/es/recommend-histories"
    params = {
        "userId": user_id or None,
        "policyVersion": policy_version or None,
        "keyword": keyword or None,
        "from": date_from or None,
        "to": date_to or None,
        "page": page,
        "size": size,
    }
    resp = requests.get(
        url,
        headers=_headers(request),
        params=params,
        timeout=settings.SPRING_TIMEOUT_SECS,
    )
    resp.raise_for_status()
    return unwrap_api_response(resp)


def post_recommendation_es_reindex(request):
    url = f"{settings.SPRING_BASE_URL}/api/admin/es/reindex"
    resp = requests.post(url, headers=_headers(request), timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return unwrap_api_response(resp)
