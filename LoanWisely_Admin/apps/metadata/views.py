from django.shortcuts import render, redirect
from apps.common.responses import render_request_exception
from apps.common.pagination import paginate
from requests import RequestException
from . import services


def credit_meta_list(request):
    try:
        data = services.get_credit_meta_list(request)
    except RequestException as exc:
        return render_request_exception(request, exc)
    items = data.get("items") if isinstance(data, dict) else data
    context = paginate(request, items, per_page=20)
    return render(request, "metadata/credit_list.html", context)


def credit_meta_create(request):
    if request.method != "POST":
        return redirect("credit_meta_list")
    try:
        version_label = request.POST.get("version_label") or None
        base_version_id = request.POST.get("base_version_id") or None
        services.create_credit_meta_version(request, version_label, base_version_id)
    except RequestException as exc:
        return render_request_exception(request, exc)
    return redirect("credit_meta_list")


def credit_meta_approve(request, version_id):
    if request.method != "POST":
        return redirect("credit_meta_list")
    try:
        services.approve_credit_meta_version(request, version_id)
    except RequestException as exc:
        return render_request_exception(request, exc)
    return redirect("credit_meta_list")


def financial_meta_list(request):
    try:
        data = services.get_financial_meta_list(request)
    except RequestException as exc:
        return render_request_exception(request, exc)
    items = data.get("items") if isinstance(data, dict) else data
    context = paginate(request, items, per_page=20)
    return render(request, "metadata/financial_list.html", context)


def financial_meta_create(request):
    if request.method != "POST":
        return redirect("financial_meta_list")
    try:
        version_label = request.POST.get("version_label") or None
        services.create_financial_meta_version(request, version_label)
    except RequestException as exc:
        return render_request_exception(request, exc)
    return redirect("financial_meta_list")


def financial_meta_approve(request, version_id):
    if request.method != "POST":
        return redirect("financial_meta_list")
    try:
        services.approve_financial_meta_version(request, version_id)
    except RequestException as exc:
        return render_request_exception(request, exc)
    return redirect("financial_meta_list")
