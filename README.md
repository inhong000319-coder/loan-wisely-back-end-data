
---

### 2) `LoanWisely_Admin` (Django) README용

```markdown
# LoanWisely Admin

Spring API를 호출해 동작하는 관리자 콘솔입니다.  
관리자 화면 자체에서 DB를 직접 접근하지 않고, 토큰 기반으로 Spring의 관리자 API를 프록시/연동합니다.

## 핵심 역할
- 관리자 로그인/세션 인증 처리
- 정책 목록/상세 조회 및 승인/배포 관리
- 원시파일 업로드, 정규화, EDA, 품질 이슈 확인
- 추천 로그/거부사유/필터 결과 조회
- 감사 로그/권한 기반 운영 화면 제공

## 아키텍처
- Django + Django Templates
- SSR 기반 템플릿 렌더링
- JWT 미들웨어 인증
- 외부 API 호출 전용 클라이언트 계층(`apps/*/client.py`)
- Spring Base URL 기반 프록시/브릿지 구조

## Django 구조
- apps/ : 도메인별 기능(auth/policies/rawfiles/approvals/audits/recommendations/metadata)
- templates/ : 서버 렌더링 HTML
- static/ : 정적 자산
- config/ : settings/{base,dev,prod}.py, URL 설정

