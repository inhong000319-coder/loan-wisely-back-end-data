import requests
import logging
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
    api_key_header = getattr(settings, "SPRING_API_KEY_HEADER", "X-API-KEY")
    api_key_value = getattr(settings, "SPRING_API_KEY", "") or "dev-temp-key"
    return {
        "Authorization": _auth_header(request),
        "X-Trace-Id": getattr(request, "trace_id", ""),
        "X-Source": "django-admin",
        api_key_header: api_key_value,
    }


def list_credit_meta(request, params=None):
    url = f"{settings.SPRING_BASE_URL}/api/admin/metadata/credit-dictionary/versions"
    resp = requests.get(url, headers=_headers(request), params=params, timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return unwrap_api_response(resp)

def get_active_credit_meta(request):
    url = f"{settings.SPRING_BASE_URL}/api/metadata/credit-dictionary/versions/active"
    headers = _headers(request)
    logging.getLogger(__name__).info(
        "Spring 호출 헤더 확인. apiKeyHeader=%s, apiKeyLen=%s",
        getattr(settings, "SPRING_API_KEY_HEADER", "X-API-KEY"),
        len(headers.get(getattr(settings, "SPRING_API_KEY_HEADER", "X-API-KEY"), "")),
    )
    resp = requests.get(url, headers=headers, timeout=settings.SPRING_TIMEOUT_SECS)
    if resp.status_code // 100 != 2:
        logging.getLogger(__name__).warning(
            "활성 메타데이터 조회 실패. status=%s, body=%s",
            resp.status_code,
            resp.text,
        )
    resp.raise_for_status()
    return unwrap_api_response(resp)


def list_financial_meta(request, params=None):
    url = f"{settings.SPRING_BASE_URL}/api/admin/metadata/financial-meta/versions"
    resp = requests.get(url, headers=_headers(request), params=params, timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return unwrap_api_response(resp)
