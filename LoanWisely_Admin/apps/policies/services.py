from django.conf import settings
from . import client


def _mock_policy_list():
    return [
        {
            "id": "POL-2026-0001",
            "name": "기본 리스크 정책",
            "version": "v3",
            "status": "APPROVED",
            "updated_at": "2026-02-05 11:30",
            "author": "writer01",
        },
        {
            "id": "POL-2026-0002",
            "name": "청년 우대 정책",
            "version": "v2",
            "status": "DRAFT",
            "updated_at": "2026-02-04 18:05",
            "author": "writer02",
        },
    ]


def _mock_policy_detail(policy_id):
    return {
        "id": policy_id,
        "name": "기본 리스크 정책",
        "version": "v3",
        "status": "APPROVED",
        "description": "LV1~LV3 입력 기반 리스크 스코어 정책",
        "rules": [
            "LV1 필수",
            "LV2/LV3 미제공 시 결측 규칙 적용",
        ],
        "validation_rules": [
            "나이 19~80",
            "연소득 0~1,000,000,000",
        ],
        "approved_by": "approver01",
        "approved_at": "2026-02-05 10:15",
        "created_at": "2026-02-01 09:00",
    }


def get_policy_list(request, params=None):
    if settings.USE_MOCK_DATA:
        return _mock_policy_list()
    return client.list_policies(request, params=params)


def get_policy_detail(request, policy_id):
    if settings.USE_MOCK_DATA:
        return _mock_policy_detail(policy_id)
    return client.get_policy(request, policy_id)


def create_policy(request, payload):
    if settings.USE_MOCK_DATA:
        return {"id": "POL-2026-NEW", "status": "DRAFT", **payload}
    return client.create_policy(request, payload)


def update_policy(request, policy_id, payload):
    if settings.USE_MOCK_DATA:
        data = _mock_policy_detail(policy_id)
        data.update(payload)
        return data
    return client.update_policy(request, policy_id, payload)


def approve_policy(request, policy_id):
    if settings.USE_MOCK_DATA:
        return {"policy_id": policy_id, "status": "APPROVED"}
    return client.approve_policy(request, policy_id)


def deploy_policy(request, policy_id):
    if settings.USE_MOCK_DATA:
        return {"policy_id": policy_id, "status": "DEPLOYED"}
    return client.deploy_policy(request, policy_id)
