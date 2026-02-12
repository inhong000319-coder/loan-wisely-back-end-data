from django.conf import settings
from . import client
from datetime import datetime


_financial_meta_versions = [
    {"version_id": 1, "status": "APPROVED", "updated_at": "2026-02-05 08:00"},
    {"version_id": 2, "status": "DRAFT", "updated_at": "2026-02-03 17:30"},
]


def _mock_credit_meta_list():
    return [
        {"version_id": "CR-2026-001", "status": "APPROVED", "updated_at": "2026-02-05 09:20"},
        {"version_id": "CR-2026-002", "status": "DRAFT", "updated_at": "2026-02-04 14:10"},
    ]


def _mock_financial_meta_list():
    return _financial_meta_versions


def get_credit_meta_list(request, params=None):
    if settings.USE_MOCK_DATA:
        return _mock_credit_meta_list()
    return client.list_credit_meta(request, params=params)

def get_active_credit_meta(request):
    if settings.USE_MOCK_DATA:
        return {"activeVersion": None}
    return client.get_active_credit_meta(request)


def get_financial_meta_list(request, params=None):
    if settings.USE_MOCK_DATA:
        return _mock_financial_meta_list()
    return client.list_financial_meta(request, params=params)


def create_financial_meta_version(base_version_id=None, version_label=None):
    next_id = max([v["version_id"] for v in _financial_meta_versions], default=0) + 1
    _financial_meta_versions.insert(0, {
        "version_id": next_id,
        "status": "DRAFT",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "base_version_id": base_version_id,
        "version_label": version_label,
    })
    return {"versionId": next_id}


def approve_financial_meta_version(version_id):
    target = None
    for item in _financial_meta_versions:
        if int(item["version_id"]) == int(version_id):
            target = item
            break

    if target is None:
        return None

    for item in _financial_meta_versions:
        if item.get("status") == "APPROVED":
            item["status"] = "INACTIVE"

    target["status"] = "APPROVED"
    target["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"approvedVersionId": int(version_id)}
