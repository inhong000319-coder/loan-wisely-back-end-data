from django.shortcuts import render, redirect
from django.contrib import messages
from apps.common.responses import render_request_exception
from requests import RequestException
from . import services


def rawfile_list(request):
    try:
        data = services.get_raw_files(request)
    except RequestException as exc:
        return render_request_exception(request, exc)
    return render(request, "rawfiles/list.html", {"items": data})


def rawfile_upload(request):
    if request.method == "POST":
        try:
            result = services.upload_raw_file(request, files=request.FILES)
        except RequestException as exc:
            return render_request_exception(request, exc)
        return render(request, "rawfiles/upload.html", {"result": result})
    return render(request, "rawfiles/upload.html")


def rawfile_validate(request, upload_id):
    if request.method != "POST":
        return redirect("/management/raw-files/")
    try:
        result = services.validate_raw_file(request, upload_id)
    except RequestException as exc:
        return render_request_exception(request, exc)
    if result.get("ok", True):
        messages.success(request, "검증이 완료되었습니다.")
    else:
        errors = result.get("errors") or []
        messages.error(request, f"검증 실패: {', '.join(errors)}")
    return redirect("/management/raw-files/")


def rawfile_ingest(request, upload_id):
    if request.method != "POST":
        return redirect("/management/raw-files/")
    try:
        result = services.ingest_raw_file(request, upload_id)
    except RequestException as exc:
        return render_request_exception(request, exc)
    inserted = result.get("inserted", 0)
    messages.success(request, f"적재 완료 (inserted={inserted})")
    return redirect("/management/raw-files/")
