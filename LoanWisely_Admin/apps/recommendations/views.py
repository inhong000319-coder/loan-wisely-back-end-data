from django.shortcuts import render
from requests import RequestException
from apps.common.responses import render_request_exception
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
