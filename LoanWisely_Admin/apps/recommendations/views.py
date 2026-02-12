from django.shortcuts import render
from requests import RequestException
from apps.common.responses import render_request_exception
from apps.common.pagination import paginate
from . import services


def recommendation_detail(request):
    recommendation_id = request.GET.get("id", "").strip()
    detail = None
    if recommendation_id:
        try:
            detail = services.fetch_recommendation_detail(request, recommendation_id)
        except RequestException as exc:
            return render_request_exception(request, exc)

    return render(
        request,
        "recommendations/detail.html",
        {
            "recommendation_id": recommendation_id,
            "detail": detail,
        },
    )


def event_logs(request):
    product_id = request.GET.get("product_id", "").strip()
    logs = None
    if product_id:
        try:
            logs = services.fetch_event_logs(request, product_id)
        except RequestException as exc:
            return render_request_exception(request, exc)

    context = paginate(request, logs, per_page=20) if logs is not None else {"items": None}
    context.update({"product_id": product_id, "logs": context.get("items")})
    return render(request, "recommendations/event_logs.html", context)


def reject_logs(request):
    request_id = request.GET.get("request_id", "").strip()
    logs = None
    if request_id:
        try:
            logs = services.fetch_reject_logs(request, request_id)
        except RequestException as exc:
            return render_request_exception(request, exc)

    context = paginate(request, logs, per_page=20) if logs is not None else {"items": None}
    context.update({"request_id": request_id, "logs": context.get("items")})
    return render(request, "recommendations/reject_logs.html", context)


def exclusion_reasons(request):
    result_id = request.GET.get("result_id", "").strip()
    reasons = None
    if result_id:
        try:
            reasons = services.fetch_exclusion_reasons(request, result_id)
        except RequestException as exc:
            return render_request_exception(request, exc)

    context = paginate(request, reasons, per_page=20) if reasons is not None else {"items": None}
    context.update({"result_id": result_id, "reasons": context.get("items")})
    return render(request, "recommendations/exclusion_reasons.html", context)
