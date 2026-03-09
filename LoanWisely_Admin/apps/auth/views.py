from django.shortcuts import render, redirect
from django.conf import settings
from requests import RequestException
from apps.common.responses import render_upstream_error
from .client import login_admin


def login_view(request):
    if request.method == "GET":
        return render(request, "auth/login.html")

    username = request.POST.get("username", "")
    password = request.POST.get("password", "")
    next_url = request.POST.get("next") or request.GET.get("next") or f"{settings.MANAGEMENT_BASE_PATH}/dashboard/"

    try:
        result = login_admin(username=username, password=password, trace_id=getattr(request, "trace_id", ""))
    except RequestException:
        return render_upstream_error(request)
    except Exception:
        return render(request, "auth/login.html", {"error": "로그인 실패"})

    token = result.get("accessToken") or result.get("token")
    if not token:
        return render(request, "auth/login.html", {"error": "토큰 발급 실패"})

    response = redirect(next_url)
    response.set_cookie(settings.JWT_COOKIE_NAME, token, httponly=True, samesite="Lax")
    return response


def logout_view(request):
    response = redirect(f"{settings.MANAGEMENT_BASE_PATH}/auth/login")
    response.delete_cookie(settings.JWT_COOKIE_NAME)
    return response
