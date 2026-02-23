# Admin API Spec (Draft, Mock)

This document defines **temporary JSON structures** for Django Admin integration.
Replace with final Spring responses when available.

## Auth

### POST /api/admin/auth/login
**Request**
```json
{
  "username": "admin01",
  "password": "********"
}
```
**Response**
```json
{
  "accessToken": "jwt-token",
  "expiresIn": 3600
}
```

### POST /api/admin/auth/verify
**Response**
```json
{
  "id": "admin01",
  "roles": ["POLICY_APPROVER"],
  "display_name": "관리자01"
}
```

---

## Policies

### GET /api/admin/policies
**Response**
```json
[
  {
    "id": "POL-2026-0001",
    "name": "기본 리스크 정책",
    "version": "v3",
    "status": "APPROVED",
    "updated_at": "2026-02-05 11:30",
    "author": "writer01"
  }
]
```

### GET /api/admin/policies/{id}
**Response**
```json
{
  "id": "POL-2026-0001",
  "name": "기본 리스크 정책",
  "version": "v3",
  "status": "APPROVED",
  "description": "LV1~LV3 입력 기반 리스크 스코어 정책",
  "rules": ["LV1 필수", "LV2/LV3 미제공 시 결측 규칙 적용"],
  "validation_rules": ["나이 19~80", "연소득 0~1,000,000,000"],
  "approved_by": "approver01",
  "approved_at": "2026-02-05 10:15",
  "created_at": "2026-02-01 09:00"
}
```

### POST /api/admin/policies/{id}/approve
**Response**
```json
{ "policy_id": "POL-2026-0001", "status": "APPROVED" }
```

### POST /api/admin/policies/{id}/deploy
**Response**
```json
{ "policy_id": "POL-2026-0001", "status": "DEPLOYED" }
```

---

## Metadata (Credit)

### GET /api/admin/metadata/credit-dictionary/versions
**Response**
```json
[
  { "version_id": "CR-2026-001", "status": "APPROVED", "updated_at": "2026-02-05 09:20" }
]
```

### POST /api/admin/metadata/credit-dictionary/versions/{versionId}/approve
**Response**
```json
{ "version_id": "CR-2026-001", "status": "APPROVED" }
```

---

## Metadata (Financial)

### GET /api/admin/metadata/financial-meta/versions
**Response**
```json
[
  { "version_id": "FN-2026-010", "status": "APPROVED", "updated_at": "2026-02-05 08:00" }
]
```

### POST /api/admin/metadata/financial-meta/versions/{versionId}/approve
**Response**
```json
{ "version_id": "FN-2026-010", "status": "APPROVED" }
```

---

## Approvals

### GET /api/admin/approvals
**Response**
```json
[
  { "target_id": "POL-2026-0002", "type": "POLICY", "status": "PENDING", "requested_at": "2026-02-05 09:10" }
]
```

### GET /api/admin/approvals/{targetId}
**Response**
```json
{
  "target_id": "POL-2026-0002",
  "type": "POLICY",
  "status": "PENDING",
  "requested_by": "writer02",
  "requested_at": "2026-02-05 09:10"
}
```

### POST /api/admin/approvals/{targetId}/approve
**Request**
```json
{ "reason": "검토 완료" }
```
**Response**
```json
{ "target_id": "POL-2026-0002", "status": "APPROVED" }
```

### POST /api/admin/approvals/{targetId}/reject
**Request**
```json
{ "reason": "규정 미충족" }
```
**Response**
```json
{ "target_id": "POL-2026-0002", "status": "REJECTED" }
```

---

## Audits

### GET /api/admin/audit/summary
**Response**
```json
[
  { "actor": "approver01", "action": "APPROVE", "target": "POL-2026-0001", "at": "2026-02-05 10:15" }
]
```

---

## Raw Files

### GET /api/admin/raw-files
**Response**
```json
[
  { "id": "RAW-001", "name": "credit_input_2026_02.csv", "status": "UPLOADED", "uploaded_at": "2026-02-05 09:00" }
]
```

### POST /api/admin/raw-files
**Response**
```json
{ "status": "UPLOADED", "file_count": 1 }
```
