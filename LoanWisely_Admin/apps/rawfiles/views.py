from django.shortcuts import render
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
