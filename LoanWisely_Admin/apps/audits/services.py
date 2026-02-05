from django.conf import settings
from . import client


def _mock_audit_summary():
    return [
        {"actor": "approver01", "action": "APPROVE", "target": "POL-2026-0001", "at": "2026-02-05 10:15"},
        {"actor": "writer02", "action": "EDIT", "target": "POL-2026-0002", "at": "2026-02-04 18:05"},
    ]


def get_audit_summary(request, params=None):
    if settings.USE_MOCK_DATA:
        return _mock_audit_summary()
    return client.list_audits(request, params=params)
