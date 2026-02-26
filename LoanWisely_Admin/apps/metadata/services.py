from django.conf import settings
from . import client


def _mock_credit_meta_list():
    return [
        {"version_id": "CR-2026-001", "status": "APPROVED", "updated_at": "2026-02-05 09:20"},
        {"version_id": "CR-2026-002", "status": "DRAFT", "updated_at": "2026-02-04 14:10"},
    ]


def _mock_financial_meta_list():
    return [
        {"version_id": "FN-2026-010", "status": "APPROVED", "updated_at": "2026-02-05 08:00"},
        {"version_id": "FN-2026-011", "status": "DRAFT", "updated_at": "2026-02-03 17:30"},
    ]


def get_credit_meta_list(request, params=None):
    if settings.USE_MOCK_DATA:
        return _mock_credit_meta_list()
    return client.list_credit_meta(request, params=params)


def get_financial_meta_list(request, params=None):
    if settings.USE_MOCK_DATA:
        return _mock_financial_meta_list()
    return client.list_financial_meta(request, params=params)


def create_credit_meta_version(request, version_label=None, base_version_id=None):
    if settings.USE_MOCK_DATA:
        return {"version_id": "CR-MOCK-001", "status": "DRAFT"}
    payload = {
        "version_label": version_label,
        "base_version_id": base_version_id,
    }
    return client.create_credit_meta_version(request, payload)


def approve_credit_meta_version(request, version_id):
    if settings.USE_MOCK_DATA:
        return {"version_id": version_id, "status": "APPROVED"}
    return client.approve_credit_meta_version(request, version_id)


def create_financial_meta_version(request, version_label=None):
    if settings.USE_MOCK_DATA:
        return {"version_id": "FN-MOCK-001", "status": "DRAFT"}
    payload = {
        "version_label": version_label,
    }
    return client.create_financial_meta_version(request, payload)


def approve_financial_meta_version(request, version_id):
    if settings.USE_MOCK_DATA:
        return {"version_id": version_id, "status": "APPROVED"}
    return client.approve_financial_meta_version(request, version_id)
