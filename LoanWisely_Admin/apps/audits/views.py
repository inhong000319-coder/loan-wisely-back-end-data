from django.shortcuts import render
from apps.common.permissions import require_roles, ROLE_AUDITOR, ROLE_SUPER_ADMIN
from apps.common.responses import render_request_exception
from apps.common.pagination import paginate
from requests import RequestException
from . import services


@require_roles(ROLE_AUDITOR, ROLE_SUPER_ADMIN)
def audit_list(request):
    try:
        data = services.get_audit_summary(request)
    except RequestException as exc:
        return render_request_exception(request, exc)
    items = data.get("items") if isinstance(data, dict) else data
    context = paginate(request, items, per_page=20)
    return render(request, "audits/list.html", context)
