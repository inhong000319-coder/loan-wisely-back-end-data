import requests
from django.conf import settings
from apps.common.api import unwrap_api_response


def login_admin(username: str, password: str, trace_id: str):
    url = f"{settings.SPRING_BASE_URL}{settings.SPRING_ADMIN_LOGIN_PATH}"
    headers = {
        "X-Trace-Id": trace_id,
        "X-Source": "django-admin",
    }
    payload = {"username": username, "password": password}

    resp = requests.post(url, json=payload, headers=headers, timeout=settings.SPRING_TIMEOUT_SECS)
    if resp.status_code != 200:
        raise ValueError("Login failed")
    return unwrap_api_response(resp)


def verify_admin_token(token: str, trace_id: str):
    url = f"{settings.SPRING_BASE_URL}{settings.SPRING_ADMIN_VERIFY_PATH}"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Trace-Id": trace_id,
        "X-Source": "django-admin",
    }

    resp = requests.post(url, headers=headers, timeout=settings.SPRING_TIMEOUT_SECS)
    if resp.status_code != 200:
        raise ValueError("Token verification failed")

    return unwrap_api_response(resp)

