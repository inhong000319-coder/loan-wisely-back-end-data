from django.http import JsonResponse
import logging
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

