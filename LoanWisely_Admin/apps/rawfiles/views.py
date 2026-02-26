from django.shortcuts import render, redirect
from django.contrib import messages
from apps.common.responses import render_request_exception
from apps.common.pagination import paginate
from requests import RequestException
from . import services


def rawfile_list(request):
    try:
        data = services.get_raw_files(request)
    except RequestException as exc:
        return render_request_exception(request, exc)
    items = data.get("items") if isinstance(data, dict) else data
    context = paginate(request, items, per_page=20)
    return render(request, "rawfiles/list.html", context)


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
def rawfile_normalize(request, upload_id):
    if request.method != "POST":
        return redirect("/management/raw-files/")
    try:
        result = services.normalize_raw_file(request, upload_id)
    except RequestException as exc:
        return render_request_exception(request, exc)
    normalized = result.get("normalized", result.get("normalizedCount", 0))
    messages.success(request, f"Normalize completed (count={normalized})")
    return redirect("/management/raw-files/")


def rawfile_eda(request, upload_id):
    if request.method != "POST":
        return redirect("/management/raw-files/")
    try:
        result = services.eda_raw_file(request, upload_id)
    except RequestException as exc:
        return render_request_exception(request, exc)
    eda_run_id = result.get("edaRunId") or result.get("eda_run_id")
    messages.success(request, f"EDA completed (run_id={eda_run_id})")
    return redirect("/management/raw-files/")

