# Notion API 연동 (문서/템플릿 자동 생성)

LOAN WISELY 프로젝트에서 Notion 페이지/데이터베이스 템플릿을 자동 생성하기 위한 설정 가이드입니다.

## 1. Notion Integration 생성

1. Notion에서 `Settings & members` -> `Connections` (또는 `Integrations`)로 이동
2. `New integration` 생성
3. 이름 예시: `LoanWisely Automation`
4. 생성 후 `Internal Integration Token` 복사

## 2. 대상 페이지에 권한 부여

자동으로 템플릿을 생성할 상위 페이지를 열고:

1. `Share`
2. 생성한 Integration (`LoanWisely Automation`) 추가

권한이 없으면 Notion API에서 403/404가 반환됩니다.

## 3. 상위 페이지 ID 확인

Notion 페이지 URL 예시:

`https://www.notion.so/workspace/abcdef1234567890abcdef1234567890?pvs=4`

위의 32자리 문자열이 `page_id`입니다.

## 4. 환경변수 설정

PowerShell 예시:

```powershell
$env:NOTION_TOKEN="secret_xxx"
$env:NOTION_PARENT_PAGE_ID="abcdef1234567890abcdef1234567890"
$env:NOTION_API_VERSION="2022-06-28"
```

## 5. 템플릿 자동 생성 실행

작업 위치:

```powershell
cd C:\workspace\Django_Spring\LoanWisely_Admin\scripts
```

전체(허브 페이지 + 테스트 시나리오 DB) 생성:

```powershell
python notion_seed_templates.py --mode all --prefix "LOAN WISELY"
```

허브 페이지만 생성:

```powershell
python notion_seed_templates.py --mode hub-page --prefix "LOAN WISELY"
```

테스트 시나리오 DB만 생성:

```powershell
python notion_seed_templates.py --mode test-db --prefix "LOAN WISELY"
```

트러블슈팅 문서(1~17) 페이지만 생성:

```powershell
python notion_seed_templates.py --mode troubleshooting-page --prefix "LOAN WISELY"
```

## 6. 생성되는 템플릿

- `LOAN WISELY 운영 허브` (페이지)
  - 운영 체크리스트/참고 링크용 기본 블록 템플릿
- `LOAN WISELY 테스트 시나리오` (데이터베이스)
  - `Scenario ID`, `Title`, `Status`, `Priority`, `Scope` 등 기본 컬럼 포함
- `LOAN WISELY 트러블슈팅 가이드 (1~17)` (페이지)
  - 프로젝트 이슈 1~17번을 증상/원인/해결/재발 방지 기준으로 정리

## 7. 커스터마이징

템플릿 정의 파일:

- `LoanWisely_Admin/scripts/notion_templates/hub_page_children.json`
- `LoanWisely_Admin/scripts/notion_templates/test_scenario_db_properties.json`

컬럼 구조/문구를 수정한 뒤 스크립트를 다시 실행하면 됩니다.

## 8. 다음 단계 (권장)

현재 스크립트는 **템플릿 생성**까지 지원합니다.  
추가로 원하면 아래도 확장 가능합니다.

- `CCKSY_LW_TC_260220.xlsx` -> CSV -> Notion DB 항목 업서트
- 테스트 결과(PASS/FAIL/BLOCK) 자동 반영
- 배포 체크리스트/장애 리포트 페이지 자동 생성

## 9. 테스트 시나리오 DB 샘플 행 채우기 (초기 데이터)

테스트 시나리오 DB를 생성한 뒤, 프로젝트 기준 샘플 시나리오(회원가입/로그인/추천/보안/관리자 파이프라인 등)를 넣을 수 있습니다.

환경변수 설정:

```powershell
$env:NOTION_TOKEN="secret_xxx"
$env:NOTION_TEST_DB_ID="생성된_테스트_DB_ID"
```

실행:

```powershell
cd C:\workspace\Django_Spring\LoanWisely_Admin\scripts
python notion_seed_test_scenarios.py --database-id $env:NOTION_TEST_DB_ID --skip-existing
```

옵션:

- `--skip-existing`: 동일 `Scenario ID`가 이미 있으면 중복 생성하지 않음
- `--owner QA`: 기본 담당자 값 변경 가능
