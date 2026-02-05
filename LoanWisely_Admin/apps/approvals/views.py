from django.shortcuts import render, redirect
from django.contrib import messages
from apps.common.permissions import require_roles, ROLE_POLICY_APPROVER, ROLE_SUPER_ADMIN
from apps.common.responses import render_request_exception
from requests import RequestException
from . import services


def approval_list(request):
    try:
        data = services.get_approvals(request)
    except RequestException as exc:
        return render_request_exception(request, exc)
    return render(request, "approvals/list.html", {"items": data})


@require_roles(ROLE_POLICY_APPROVER, ROLE_SUPER_ADMIN)
def approval_detail(request, target_id):
    if request.method == "POST":
        action = request.POST.get("action")
        reason = request.POST.get("reason", "")

        if not reason.strip():
            return _render_with_status(request, target_id, error_message="사유는 필수입니다.")

        try:
            if action == "approve":
                services.approve_target(request, target_id, reason=reason)
                messages.success(request, "승인 완료")
                return redirect("/management/approvals/")
            if action == "reject":
                services.reject_target(request, target_id, reason=reason)
                messages.success(request, "반려 완료")
                return redirect("/management/approvals/")
        except RequestException as exc:
            return render_request_exception(request, exc)
        except Exception:
            return _render_with_status(request, target_id, error_message="요청 처리에 실패했습니다.")

    return _render_with_status(request, target_id)


def _render_with_status(request, target_id, success_message=None, error_message=None):
    try:
        data = services.get_approval_detail(request, target_id)
    except RequestException as exc:
        return render_request_exception(request, exc)

    context = {"approval": data, "target_id": target_id}
    if success_message:
        context["success_message"] = success_message
    if error_message:
        context["error_message"] = error_message
    return render(request, "approvals/detail.html", context)
