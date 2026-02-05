from django.shortcuts import render
from apps.common.responses import render_request_exception
from requests import RequestException
from . import services


def credit_meta_list(request):
    try:
        data = services.get_credit_meta_list(request)
    except RequestException as exc:
        return render_request_exception(request, exc)
    return render(request, "metadata/credit_list.html", {"items": data})


def financial_meta_list(request):
    try:
        data = services.get_financial_meta_list(request)
    except RequestException as exc:
        return render_request_exception(request, exc)
    return render(request, "metadata/financial_list.html", {"items": data})
