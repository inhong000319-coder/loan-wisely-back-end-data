from django.shortcuts import render, redirect
from django.contrib import messages
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


def recommendation_es_search(request):
    user_id = request.GET.get("user_id", "").strip()
    login_id = request.GET.get("login_id", "").strip()
    policy_version = request.GET.get("policy_version", "").strip()
    keyword = request.GET.get("keyword", "").strip()
    date_from = request.GET.get("from", "").strip()
    date_to = request.GET.get("to", "").strip()
    page = request.GET.get("page", "0").strip()
    size = request.GET.get("size", "20").strip()

    result = None
    if any([user_id, login_id, policy_version, keyword, date_from, date_to]):
        try:
            result = services.fetch_recommendation_es_search(
                request,
                user_id=user_id,
                login_id=login_id,
                policy_version=policy_version,
                keyword=keyword,
                date_from=date_from,
                date_to=date_to,
                page=page,
                size=size,
            )
        except RequestException as exc:
            return render_request_exception(request, exc)

    context = {
        "user_id": user_id,
        "login_id": login_id,
        "policy_version": policy_version,
        "keyword": keyword,
        "date_from": date_from,
        "date_to": date_to,
        "page": page,
        "size": size,
        "result": result,
    }
    return render(request, "recommendations/es_search.html", context)


def recommendation_es_reindex(request):
    if request.method != "POST":
        return redirect("/management/recommendations/es-search")
    try:
        result = services.fetch_recommendation_es_reindex(request)
    except RequestException as exc:
        return render_request_exception(request, exc)

    policy_count = result.get("recoPolicyCount", 0) if isinstance(result, dict) else 0
    history_count = result.get("recommendHistoryCount", 0) if isinstance(result, dict) else 0
    messages.success(request, f"ES 재색인 완료 (policies={policy_count}, histories={history_count})")
    return redirect("/management/recommendations/es-search")
