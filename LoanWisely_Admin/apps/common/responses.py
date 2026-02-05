from requests import RequestException
from django.shortcuts import render, redirect
from django.conf import settings


def json_error(message: str, status: int = 400):
    from django.http import JsonResponse
    return JsonResponse({"error": message}, status=status)


def render_error(request, message: str, status: int = 400):
    return render(request, "base/error.html", {"message": message}, status=status)


def render_upstream_error(request, message: str = "Upstream service error", status: int = 502):
    return render(request, "base/error.html", {"message": message}, status=status)


def render_request_exception(request, exc: RequestException):
    response = getattr(exc, "response", None)
    if response is None:
        return render_upstream_error(request, message="서비스에 연결할 수 없습니다.")

    if response.status_code == 401:
        login_url = f"{settings.MANAGEMENT_BASE_PATH}/auth/login"
        return redirect(login_url)
    if response.status_code == 403:
        return render_error(request, "권한이 없습니다.", status=403)
    if response.status_code >= 500:
        return render_error(request, "서버 오류가 발생했습니다.", status=502)

    return render_upstream_error(request)
