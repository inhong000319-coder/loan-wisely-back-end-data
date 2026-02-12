from django.http import JsonResponse
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from apps.metadata import services as metadata_services


def health(request):
    return JsonResponse({"status": "ok"})


def active_metadata(request):
    active_version = None
    try:
        data = metadata_services.get_active_credit_meta(request) or {}
        if isinstance(data, dict):
            active_version = data.get("activeVersion")
    except Exception:
        logging.getLogger(__name__).warning("활성 메타데이터 조회 중 예외 발생")
        active_version = None
    return JsonResponse({"activeVersion": active_version})


@csrf_exempt
def create_financial_meta_version(request):
    if request.method != "POST":
        return JsonResponse({"message": "Method Not Allowed"}, status=405)

    payload = {}
    try:
        if request.body:
            payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        payload = {}

    result = metadata_services.create_financial_meta_version(
        payload.get("baseVersionId"),
        payload.get("versionLabel"),
    )
    return JsonResponse(result)


@csrf_exempt
def approve_financial_meta_version(request, version_id):
    if request.method != "POST":
        return JsonResponse({"message": "Method Not Allowed"}, status=405)

    result = metadata_services.approve_financial_meta_version(version_id)
    if result is None:
        return JsonResponse({"message": "version not found"}, status=404)
    return JsonResponse(result)
