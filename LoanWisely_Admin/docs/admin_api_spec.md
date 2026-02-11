# Admin/Policy/Meta API 스캐폴딩 설계 (설계서 기준)

본 문서는 **설계서(7. API 명세서.pdf)** 기준으로 Admin/Policy/Meta 관련 API의 스캐폴딩(구조/엔드포인트/핵심 책임)을 정리한다.
최종 Spring 응답 스키마 확정 시 이 문서는 해당 스키마로 교체한다.

## 1) 메타데이터 (Credit Dictionary)

### DM_CR_001 신용사전 버전 생성
- Method: `POST`
- Endpoint: `/api/admin/metadata/credit-dictionary/versions`
- Scope: OAUTH_ADMIN
- 요청: `baseVersionId?`
- 응답: `versionId`
- 책임: 초안 버전 생성(Draft)

### DM_CR_002 신용사전 버전 수정
- Method: `PUT`
- Endpoint: `/api/admin/metadata/credit-dictionary/versions/{versionId}`
- Scope: OAUTH_ADMIN
- 요청: `items[]`
- 응답: `versionId`
- 책임: Draft 상태에서만 수정 허용

### DM_CR_003 신용사전 버전 승인
- Method: `POST`
- Endpoint: `/api/admin/metadata/credit-dictionary/versions/{versionId}/approve`
- Scope: OAUTH_ADMIN
- 요청: -
- 응답: `approvedVersionId`
- 책임: 승인 후 불변, 엔진에서 사용 가능

### DM_CR_004 활성 신용사전 조회
- Method: `GET`
- Endpoint: `/api/metadata/credit-dictionary/versions/active`
- Scope: PUBLIC
- 응답: `activeVersion`
- 책임: 운영 중인 승인본 조회

## 2) 메타데이터 (Financial Meta)

### DM_FN_001 금융메타 버전 생성
- Method: `POST`
- Endpoint: `/api/admin/metadata/financial-meta/versions`
- Scope: OAUTH_ADMIN
- 요청: `baseVersionId?`
- 응답: `versionId`

### DM_FN_002 금융메타 버전 승인
- Method: `POST`
- Endpoint: `/api/admin/metadata/financial-meta/versions/{versionId}/approve`
- Scope: OAUTH_ADMIN
- 요청: -
- 응답: `approvedVersionId`

### DM_FN_003 활성 금융메타 조회
- Method: `GET`
- Endpoint: `/api/metadata/financial-meta/versions/active`
- Scope: PUBLIC
- 응답: `activeVersion`

## 3) 정책 관리 (Policy)

### MG_AD_EM_001 정책 생성
- Method: `POST`
- Endpoint: `/api/admin/policies`
- Scope: OAUTH_ADMIN
- 요청: `policyJson`
- 응답: `policyId`
- 책임: 정책 초안 생성

### MG_AD_EM_002 정책 승인
- Method: `POST`
- Endpoint: `/api/admin/policies/{id}/approve`
- Scope: OAUTH_ADMIN
- 요청: -
- 응답: `approvedId`
- 책임: 승인 상태 전환

### MG_AD_EM_003 정책 배포
- Method: `POST`
- Endpoint: `/api/admin/policies/{id}/deploy`
- Scope: OAUTH_ADMIN
- 요청: -
- 응답: `activePolicy`
- 책임: 운영 반영(활성화)

## 4) 원천 데이터 적재 (Raw Files)

### MG_AD_DM_001 원천 파일 업로드
- Method: `POST`
- Endpoint: `/api/admin/raw-files`
- Scope: OAUTH_ADMIN
- 요청: `file`
- 응답: `uploadId`

### MG_AD_DM_002 포맷 검증
- Method: `POST`
- Endpoint: `/api/admin/raw-files/{id}/validate`
- Scope: OAUTH_ADMIN
- 요청: -
- 응답: `validationResult`

### MG_AD_DM_003 데이터 적재
- Method: `POST`
- Endpoint: `/api/admin/raw-files/{id}/ingest`
- Scope: OAUTH_ADMIN
- 요청: `options`
- 응답: `ingestResult`

## 5) 설명/감사

### MG_RE_001 추천 설명 조회
- Method: `GET`
- Endpoint: `/api/recommendations/{id}/explain`
- Scope: OAUTH_ADMIN
- 응답: `explainPayload`

### MG_RE_002 사용자 접근 감사 조회
- Method: `GET`
- Endpoint: `/api/users/me/audit/access-logs`
- Scope: OAUTH_USER
- 응답: `logs`

### MG_RE_003 운영 감사 요약
- Method: `GET`
- Endpoint: `/api/admin/audit/summary`
- Scope: OAUTH_ADMIN
- 응답: `summary`

## 6) 패키지/클래스 스캐폴딩 제안

- `com.ccksy.loan.domain.management`
- `controller`
- `MetadataAdminController` (credit-dictionary, financial-meta)
- `PolicyAdminController`
- `RawFileAdminController`
- `AuditController`
- `service`
- `CreditDictionaryService`
- `FinancialMetaService`
- `PolicyService`
- `RawFileService`
- `AuditService`
- `dto`
- `request`
- `response`
- `entity`
- `mapper`

## 7) 진행 원칙

1. 설계서 Endpoint/Method를 우선 준수
2. 승인 전 Draft 상태에서만 수정 가능
3. 승인본은 불변
4. Engine은 승인본만 참조
