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

def get_active_credit_meta(request):
    if settings.USE_MOCK_DATA:
        return {"activeVersion": None}
    return client.get_active_credit_meta(request)


def get_financial_meta_list(request, params=None):
    if settings.USE_MOCK_DATA:
        return _mock_financial_meta_list()
    return client.list_financial_meta(request, params=params)
