from requests import RequestException
from django.shortcuts import render
from . import services


def _build_chart_data(items):
    max_count = max([item.get("count", 0) for item in items], default=0)
    chart = []
    for item in items:
        count = item.get("count", 0) or 0
        percent = int((count / max_count) * 100) if max_count else 0
        chart.append(
            {
                "date": item.get("date") or "-",
                "count": count,
                "percent": percent,
            }
        )
    return chart


def dashboard_home(request):
    dashboard_error = None
    try:
        result = services.fetch_dashboard(request)
    except RequestException as exc:
        dashboard_error = "대시보드 데이터를 불러오지 못했습니다. (임시 데이터 표시)"
        result = {
            "user_count": 41410,
            "visit_stats": [
                {"date": "2026-02-18", "count": 312},
                {"date": "2026-02-19", "count": 355},
                {"date": "2026-02-20", "count": 398},
                {"date": "2026-02-21", "count": 421},
                {"date": "2026-02-22", "count": 465},
                {"date": "2026-02-23", "count": 502},
                {"date": "2026-02-24", "count": 541},
            ],
            "new_users": [
                {"user_id": 10421, "username": "hana", "created_at": "2026-02-24 09:12"},
                {"user_id": 10419, "username": "minsu", "created_at": "2026-02-24 08:45"},
                {"user_id": 10411, "username": "yuna", "created_at": "2026-02-23 22:09"},
                {"user_id": 10405, "username": "jinho", "created_at": "2026-02-23 18:32"},
                {"user_id": 10398, "username": "soyeon", "created_at": "2026-02-23 15:04"},
            ],
        }

    if not isinstance(result, dict):
        result = {}

    user_count = result.get("user_count", 0)
    visit_stats = result.get("visit_stats", [])
    new_users = result.get("new_users", [])
    chart = _build_chart_data(visit_stats)

    context = {
        "user_count": user_count,
        "visit_stats": chart,
        "new_users": new_users,
        "dashboard_error": dashboard_error,
    }
    return render(request, "dashboard/home.html", context)
