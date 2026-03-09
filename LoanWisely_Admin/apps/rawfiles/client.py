import logging
import requests
from django.conf import settings
from apps.common.api import unwrap_api_response

logger = logging.getLogger(__name__)


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


def list_raw_files(request, params=None):
    url = f"{settings.SPRING_BASE_URL}/api/admin/raw-files"
    resp = requests.get(url, headers=_headers(request), params=params, timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return unwrap_api_response(resp)


def upload_raw_file(request, files):
    url = f"{settings.SPRING_BASE_URL}/api/admin/raw-files"
    resp = requests.post(url, headers=_headers(request), files=files, timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return unwrap_api_response(resp)


def validate_raw_file(request, upload_id):
    url = f"{settings.SPRING_BASE_URL}/api/admin/raw-files/{upload_id}/validate"
    resp = requests.post(url, headers=_headers(request), timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return unwrap_api_response(resp)


def ingest_raw_file(request, upload_id):
    url = f"{settings.SPRING_BASE_URL}/api/admin/raw-files/{upload_id}/ingest"
    resp = requests.post(url, headers=_headers(request), timeout=settings.SPRING_TIMEOUT_SECS)
    resp.raise_for_status()
    return unwrap_api_response(resp)


def normalize_raw_file(request, upload_id):
    url = f"{settings.SPRING_BASE_URL}/api/admin/raw-files/{upload_id}/normalize"
    resp = requests.post(url, headers=_headers(request), timeout=settings.SPRING_TIMEOUT_SECS)
    logger.info('SPRING normalize status=%s body=%s', resp.status_code, (resp.text or '')[:2000])
    resp.raise_for_status()
    return unwrap_api_response(resp)

def eda_raw_file(request, upload_id):
    url = f"{settings.SPRING_BASE_URL}/api/admin/raw-files/{upload_id}/eda"
    resp = requests.post(url, headers=_headers(request), timeout=settings.SPRING_TIMEOUT_SECS)
    logger.info('SPRING eda status=%s body=%s', resp.status_code, (resp.text or '')[:2000])
    resp.raise_for_status()
    return unwrap_api_response(resp)



