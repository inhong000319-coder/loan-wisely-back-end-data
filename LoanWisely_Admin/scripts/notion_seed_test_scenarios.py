from __future__ import annotations

import argparse
import os
import re
from datetime import date
from typing import Any

from notion_client import NotionClient


SAMPLE_SCENARIOS: list[dict[str, Any]] = [
    {
        "scenario_id": "IT-E2E-001",
        "title": "회원가입 성공 (아이디/비밀번호 정책 충족)",
        "priority": "High",
        "scope": "React UI",
        "status": "Ready",
        "owner": "QA",
        "environment": "Local / Chrome / Spring+Next",
        "preconditions": "백엔드 및 프론트 서버 기동, 중복되지 않는 아이디 준비",
        "steps": "회원가입 페이지 접속 -> 유효한 아이디/비밀번호 입력 -> 가입 요청",
        "expected": "회원가입 성공 응답, 로그인 가능 상태",
    },
    {
        "scenario_id": "IT-SEC-001",
        "title": "비밀번호 해시 저장 확인",
        "priority": "High",
        "scope": "Security",
        "status": "Ready",
        "owner": "QA",
        "environment": "Local / Oracle",
        "preconditions": "신규 회원가입 완료 계정 1개",
        "steps": "회원가입 후 USER_AUTH.password_hash 조회",
        "expected": "평문이 아닌 BCrypt 해시 형식($2a$/$2b$) 저장",
    },
    {
        "scenario_id": "IT-API-001",
        "title": "로그인 성공 API",
        "priority": "High",
        "scope": "Spring API",
        "status": "Ready",
        "owner": "QA",
        "environment": "Local / Spring API",
        "preconditions": "유효한 사용자 계정 존재",
        "steps": "POST /api/auth/login with valid credentials",
        "expected": "200 응답, accessToken 및 만료시간 반환",
    },
    {
        "scenario_id": "IT-API-002",
        "title": "로그인 실패 횟수 누적 및 잠금 이후 누적 확인",
        "priority": "High",
        "scope": "Spring API",
        "status": "Ready",
        "owner": "QA",
        "environment": "Local / Spring API / Oracle",
        "preconditions": "테스트 계정 1개, 잘못된 비밀번호 준비",
        "steps": "로그인 실패 6회 이상 반복 후 USER_AUTH.fail_login_count 조회",
        "expected": "5회 초과 이후에도 fail_login_count가 계속 증가",
    },
    {
        "scenario_id": "IT-E2E-002",
        "title": "LV1 필수정보 미입력 시 추천 실행 차단",
        "priority": "High",
        "scope": "Integration",
        "status": "Ready",
        "owner": "QA",
        "environment": "Local / Chrome",
        "preconditions": "로그인 상태, 사용자 입력 페이지 접근",
        "steps": "LV1 필수값 일부 미입력 -> 추천 결과 보기 클릭",
        "expected": "추천 요청 미실행, 사용자 안내 메시지 표시",
    },
    {
        "scenario_id": "IT-E2E-003",
        "title": "금융정보 이용 동의 미체크 시 추천 실행 차단",
        "priority": "High",
        "scope": "Integration",
        "status": "Ready",
        "owner": "QA",
        "environment": "Local / Chrome",
        "preconditions": "LV1 필수값 입력 완료",
        "steps": "동의 체크 해제 상태로 추천 결과 보기 클릭",
        "expected": "추천 API 호출 차단 또는 백엔드 검증 실패 응답",
    },
    {
        "scenario_id": "IT-E2E-004",
        "title": "LV2/LV3 저장 실패 시 LV1 기반 추천 계속 진행",
        "priority": "Medium",
        "scope": "Integration",
        "status": "Ready",
        "owner": "QA",
        "environment": "Local / Chrome / Network intercept",
        "preconditions": "LV1 입력 완료, 동의 체크",
        "steps": "LV2/LV3 저장 API 실패 유도 후 추천 실행",
        "expected": "추천 결과는 생성되고, 선택정보 저장 실패만 로그/경고 처리",
    },
    {
        "scenario_id": "IT-UI-001",
        "title": "금액/숫자 입력칸 숫자만 입력 허용",
        "priority": "Medium",
        "scope": "React UI",
        "status": "Ready",
        "owner": "QA",
        "environment": "Local / Chrome",
        "preconditions": "사용자 입력 페이지 접근",
        "steps": "나이/연소득/총부채/대출건수 입력칸에 -, +, e, . 입력 시도",
        "expected": "비숫자 입력 차단 또는 즉시 제거",
    },
    {
        "scenario_id": "IT-UI-002",
        "title": "추천 결과 페이지 제외 상품 토글 및 페이지네이션",
        "priority": "Medium",
        "scope": "React UI",
        "status": "Ready",
        "owner": "QA",
        "environment": "Local / Chrome",
        "preconditions": "추천 결과 데이터 존재(제외 상품 포함)",
        "steps": "제외 상품 보기 토글 클릭 -> 페이지 전환",
        "expected": "제외 상품 목록이 토글로 노출되고 페이지네이션 정상 동작",
    },
    {
        "scenario_id": "IT-API-003",
        "title": "전체 상품 조회 API 및 페이지 표시",
        "priority": "Medium",
        "scope": "Integration",
        "status": "Ready",
        "owner": "QA",
        "environment": "Local / Spring+Next",
        "preconditions": "LOAN_PRODUCT 데이터 적재 완료",
        "steps": "전체 상품 조회 페이지 접속",
        "expected": "상품 목록/요약 패널/상세 보기 팝오버 정상 노출",
    },
    {
        "scenario_id": "IT-API-004",
        "title": "Provider URL 팝오버 데이터 노출 확인",
        "priority": "Medium",
        "scope": "Integration",
        "status": "Ready",
        "owner": "QA",
        "environment": "Local / Oracle / Chrome",
        "preconditions": "PROVIDER_URL에 fin_co_no별 URL 등록",
        "steps": "추천 또는 상품 목록에서 상세 보기 클릭",
        "expected": "은행명/대출상품/URL 정보가 팝오버에 표시",
    },
    {
        "scenario_id": "IT-API-005",
        "title": "금리 계산 규칙 (A 우선, 없으면 B+C-D)",
        "priority": "High",
        "scope": "Spring API",
        "status": "Ready",
        "owner": "QA",
        "environment": "Local / Oracle / 금감원 적재데이터",
        "preconditions": "금감원 옵션 데이터(A/B/C/D) 적재",
        "steps": "상품 조회/추천 결과 금리 확인 (A 존재/부재 케이스 비교)",
        "expected": "A 존재 시 A 사용, A 부재 시 B+C-D 계산값 사용",
    },
    {
        "scenario_id": "IT-SEC-002",
        "title": "음수/0 이하 금리 표시 보정",
        "priority": "Medium",
        "scope": "Integration",
        "status": "Ready",
        "owner": "QA",
        "environment": "Local / Chrome",
        "preconditions": "금리 계산 결과가 0 이하인 샘플 상품 존재",
        "steps": "추천 결과 카드/상세 화면 금리 영역 확인",
        "expected": "표시 규칙에 맞게 공란 또는 보정된 형식으로 노출",
    },
    {
        "scenario_id": "IT-ADMIN-001",
        "title": "원천파일 업로드/validate/ingest/normalize/eda 파이프라인",
        "priority": "High",
        "scope": "Integration",
        "status": "Ready",
        "owner": "QA",
        "environment": "Local / Admin + Spring",
        "preconditions": "관리자 로그인, 테스트 CSV 파일 준비",
        "steps": "업로드 -> validate -> ingest -> normalize -> eda 순서 실행",
        "expected": "각 단계 200 응답, 상태 전이 정상",
    },
    {
        "scenario_id": "IT-SEC-003",
        "title": "관리자 원천파일 업로드 보안 (.exe 차단)",
        "priority": "High",
        "scope": "Security",
        "status": "Ready",
        "owner": "QA",
        "environment": "Local / Admin + Spring",
        "preconditions": "관리자 로그인, .exe 테스트 파일 준비",
        "steps": "원천파일 업로드 API에 .exe 업로드 시도",
        "expected": "400/차단 응답, 서버에 파일 저장되지 않음",
    },
]


def normalize_notion_id(raw: str) -> str:
    value = (raw or "").strip()
    if not value:
        return ""
    compact = re.sub(r"[^0-9a-fA-F]", "", value)
    match = re.search(r"([0-9a-fA-F]{32})", compact)
    if match:
        hex_id = match.group(1).lower()
        return f"{hex_id[:8]}-{hex_id[8:12]}-{hex_id[12:16]}-{hex_id[16:20]}-{hex_id[20:]}"
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed sample test scenarios into a Notion database.")
    parser.add_argument(
        "--database-id",
        default=os.getenv("NOTION_TEST_DB_ID", "").strip(),
        help="Target Notion database ID (or set NOTION_TEST_DB_ID)",
    )
    parser.add_argument(
        "--owner",
        default="QA",
        help="Default owner value for seeded rows (used when row owner is missing)",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip rows whose Scenario ID already exists in the database",
    )
    return parser.parse_args()


def rich_text(value: str) -> dict[str, Any]:
    return {"rich_text": [{"type": "text", "text": {"content": value}}]}


def title_text(value: str) -> dict[str, Any]:
    return {"title": [{"type": "text", "text": {"content": value}}]}


def select_value(value: str) -> dict[str, Any]:
    return {"select": {"name": value}}


def checkbox_value(value: bool) -> dict[str, Any]:
    return {"checkbox": value}


def date_value(iso_date: str | None) -> dict[str, Any]:
    if not iso_date:
        return {"date": None}
    return {"date": {"start": iso_date}}


def scenario_to_properties(item: dict[str, Any], default_owner: str) -> dict[str, Any]:
    return {
        "Scenario ID": title_text(item["scenario_id"]),
        "Title": rich_text(item["title"]),
        "Priority": select_value(item.get("priority", "Medium")),
        "Scope": select_value(item.get("scope", "Integration")),
        "Status": select_value(item.get("status", "Ready")),
        "Owner": rich_text(item.get("owner") or default_owner),
        "Environment": rich_text(item.get("environment", "")),
        "Preconditions": rich_text(item.get("preconditions", "")),
        "Steps": rich_text(item.get("steps", "")),
        "Expected Result": rich_text(item.get("expected", "")),
        "Actual Result": rich_text(item.get("actual", "")),
        "Log Summary": rich_text(item.get("log_summary", "")),
        "Retest Required": checkbox_value(bool(item.get("retest_required", False))),
        "Executed At": date_value(item.get("executed_at")),
    }


def extract_title_plain(page: dict[str, Any], prop_name: str) -> str:
    props = page.get("properties", {})
    prop = props.get(prop_name, {})
    title_items = prop.get("title", [])
    return "".join(part.get("plain_text", "") for part in title_items).strip()


def load_existing_scenario_ids(client: NotionClient, database_id: str) -> set[str]:
    existing: set[str] = set()
    cursor: str | None = None
    while True:
        payload: dict[str, Any] = {}
        if cursor:
            payload["start_cursor"] = cursor
        result = client.query_database(database_id, payload)
        for row in result.get("results", []):
            scenario_id = extract_title_plain(row, "Scenario ID")
            if scenario_id:
                existing.add(scenario_id)
        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")
        if not cursor:
            break
    return existing


def main() -> None:
    args = parse_args()
    if not args.database_id:
        raise SystemExit("Missing database id. Use --database-id or set NOTION_TEST_DB_ID.")

    db_id = normalize_notion_id(args.database_id)
    client = NotionClient.from_env()

    existing_ids = load_existing_scenario_ids(client, db_id) if args.skip_existing else set()

    created = 0
    skipped = 0
    today = date.today().isoformat()

    for item in SAMPLE_SCENARIOS:
        scenario_id = item["scenario_id"]
        if scenario_id in existing_ids:
            skipped += 1
            print(f"- skip existing: {scenario_id}")
            continue

        row = dict(item)
        row.setdefault("executed_at", today)
        props = scenario_to_properties(row, args.owner)
        created_page = client.create_database_page(db_id, props)
        created += 1
        print(f"- created: {scenario_id} ({created_page.get('id', '')})")

    print(f"Done. created={created}, skipped={skipped}, total_seed={len(SAMPLE_SCENARIOS)}")


if __name__ == "__main__":
    main()
