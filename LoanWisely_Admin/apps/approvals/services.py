from django.conf import settings
from . import client


def _mock_approvals():
    return [
        {"target_id": "POL-2026-0002", "type": "POLICY", "status": "PENDING", "requested_at": "2026-02-05 09:10"},
        {"target_id": "CR-2026-002", "type": "CREDIT_META", "status": "PENDING", "requested_at": "2026-02-04 16:40"},
    ]


def _mock_approval_detail(target_id):
    return {
        "target_id": target_id,
        "type": "POLICY",
        "status": "PENDING",
        "requested_by": "writer02",
        "requested_at": "2026-02-05 09:10",
    }


def get_approvals(request, params=None):
    if settings.USE_MOCK_DATA:
        return _mock_approvals()
    return client.list_approvals(request, params=params)


def get_approval_detail(request, target_id):
    if settings.USE_MOCK_DATA:
        return _mock_approval_detail(target_id)
    return client.get_approval(request, target_id)


def approve_target(request, target_id, reason=""):
    if settings.USE_MOCK_DATA:
        return {"target_id": target_id, "status": "APPROVED", "reason": reason}
    return client.approve_target(request, target_id, reason=reason)


def reject_target(request, target_id, reason=""):
    if settings.USE_MOCK_DATA:
        return {"target_id": target_id, "status": "REJECTED", "reason": reason}
    return client.reject_target(request, target_id, reason=reason)
