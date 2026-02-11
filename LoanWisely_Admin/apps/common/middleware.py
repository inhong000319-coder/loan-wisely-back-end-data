import uuid
from urllib.parse import urlencode
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings

from apps.auth.client import verify_admin_token

PUBLIC_PATH_PREFIXES = (
    "/management/auth/",
    "/static/",
)


class JwtAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.trace_id = str(uuid.uuid4())

        if getattr(settings, "DISABLE_AUTH", False):
            request.actor = {"id": "dev", "roles": ["SUPER_ADMIN"]}
            request.actor_id = "dev"
            request.actor_roles = ["SUPER_ADMIN"]
            response = self.get_response(request)
            response["X-Auth-Bypass"] = "1"
            return response

        if request.path.startswith(PUBLIC_PATH_PREFIXES):
            return self.get_response(request)

        token = self._extract_token(request)
        if not token:
            query = urlencode({"next": request.get_full_path()})
            return HttpResponseRedirect(f"{settings.MANAGEMENT_BASE_PATH}/auth/login?{query}")

        try:
            actor = verify_admin_token(token, trace_id=request.trace_id)
        except Exception:
            return HttpResponseForbidden("Invalid or expired token")

        request.actor = actor
        request.actor_id = actor.get("id")
        request.actor_roles = actor.get("roles", [])

        response = self.get_response(request)
        response["X-Trace-Id"] = request.trace_id
        return response

    def _extract_token(self, request):
        header_name = getattr(settings, "JWT_HEADER_NAME", "Authorization")
        cookie_name = getattr(settings, "JWT_COOKIE_NAME", "admin_jwt")

        auth_header = request.headers.get(header_name, "")
        if auth_header.startswith("Bearer "):
            return auth_header.replace("Bearer ", "").strip()

        return request.COOKIES.get(cookie_name)
