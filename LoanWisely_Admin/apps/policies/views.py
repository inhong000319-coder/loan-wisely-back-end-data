from django.shortcuts import render, redirect
from django.contrib import messages
from apps.common.permissions import require_roles, ROLE_POLICY_APPROVER, ROLE_POLICY_WRITER, ROLE_SUPER_ADMIN
from apps.common.responses import render_request_exception
from requests import RequestException
from . import services


def policy_list(request):
    try:
        data = services.get_policy_list(request)
    except RequestException as exc:
        return render_request_exception(request, exc)
    return render(request, "policies/list.html", {"items": data})


@require_roles(ROLE_POLICY_WRITER, ROLE_SUPER_ADMIN)
def policy_create(request):
    if request.method == "POST":
        payload = {
            "name": request.POST.get("name", ""),
            "description": request.POST.get("description", ""),
            "rules": _split_lines(request.POST.get("rules", "")),
            "validation_rules": _split_lines(request.POST.get("validation_rules", "")),
        }
        try:
            data = services.create_policy(request, payload)
        except RequestException as exc:
            return render_request_exception(request, exc)
        messages.success(request, "정책이 등록되었습니다.")
        return redirect(f"/management/policies/{data.get('id')}/")
    return render(request, "policies/create.html")


def policy_detail(request, policy_id):
    can_edit = ("POLICY_WRITER" in request.actor_roles) or ("SUPER_ADMIN" in request.actor_roles)
    can_approve = ("POLICY_APPROVER" in request.actor_roles) or ("SUPER_ADMIN" in request.actor_roles)
    edit_mode = can_edit and request.GET.get("edit") == "1"

    if request.method == "POST":
        try:
            payload = {
                "description": request.POST.get("description", ""),
                "rules": _split_lines(request.POST.get("rules", "")),
                "validation_rules": _split_lines(request.POST.get("validation_rules", "")),
            }
            data = services.update_policy(request, policy_id, payload)
        except RequestException as exc:
            return render_request_exception(request, exc)
        return render(request, "policies/detail.html", {
            "policy": data,
            "policy_id": policy_id,
            "success_message": "정책 설명이 저장되었습니다.",
            "edit_mode": False,
            "can_edit": can_edit,
            "can_approve": can_approve,
        })

    try:
        data = services.get_policy_detail(request, policy_id)
    except RequestException as exc:
        return render_request_exception(request, exc)
    return render(request, "policies/detail.html", {
        "policy": data,
        "policy_id": policy_id,
        "edit_mode": edit_mode,
        "can_edit": can_edit,
        "can_approve": can_approve,
    })


@require_roles(ROLE_POLICY_APPROVER, ROLE_SUPER_ADMIN)
def policy_approve(request, policy_id):
    if request.method == "POST":
        try:
            result = services.approve_policy(request, policy_id)
        except RequestException as exc:
            return render_request_exception(request, exc)
        return render(request, "policies/approve.html", {
            "policy_id": policy_id,
            "result": result,
            "success_message": "정책이 승인되었습니다.",
        })
    return render(request, "policies/approve.html", {"policy_id": policy_id})


@require_roles(ROLE_POLICY_APPROVER, ROLE_SUPER_ADMIN)
def policy_deploy(request, policy_id):
    if request.method == "POST":
        try:
            result = services.deploy_policy(request, policy_id)
        except RequestException as exc:
            return render_request_exception(request, exc)
        return render(request, "policies/deploy.html", {
            "policy_id": policy_id,
            "result": result,
            "success_message": "정책이 배포되었습니다.",
        })
    return render(request, "policies/deploy.html", {"policy_id": policy_id})


def _split_lines(value: str):
    return [line.strip() for line in value.splitlines() if line.strip()]
