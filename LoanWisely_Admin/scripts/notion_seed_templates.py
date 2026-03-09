from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from notion_client import NotionClient, load_json_file


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = SCRIPT_DIR / "notion_templates"


TROUBLESHOOTING_ITEMS = [
    {
        "title": "1. Flyway V22 검증 실패",
        "symptom": "앱 시작 시 Validate failed / Detected failed migration to version 22 오류 발생",
        "cause": "flyway_schema_history 이력과 실제 적용 상태가 불일치(중간 실패/수동 수정)",
        "fix": "Flyway 이력과 스키마 상태를 함께 정상화하고, 새 DB에서는 통합 baseline migration으로 재시작",
        "prevention": "flyway_schema_history 직접 수정 최소화, 실패 시 이력/DB 상태를 함께 점검",
    },
    {
        "title": "2. Oracle + Flyway 히스토리 식별자 문제",
        "symptom": "ORA-00904: \"installed_rank\": 부적합한 식별자",
        "cause": "Oracle에서 히스토리 테이블/컬럼을 수동 변경해 Flyway 기대 구조와 불일치",
        "fix": "FLYWAY_SCHEMA_HISTORY를 Flyway가 생성한 구조로 유지하고 수동 rename 중지",
        "prevention": "히스토리 테이블/컬럼 수동 변경 금지, quoted identifier 혼용 금지",
    },
    {
        "title": "3. flywayRepair Gradle task 없음",
        "symptom": "Task 'flywayRepair' not found",
        "cause": "Spring Boot Auto Flyway 사용 중이며 Flyway Gradle plugin task 미구성",
        "fix": "Gradle task 대신 Spring/Flyway 상태 기준으로 조치, 필요 시 plugin 별도 추가",
        "prevention": "Flyway 운영 방식(Spring Auto/Gradle plugin) 기준 문서화",
    },
    {
        "title": "4. Non-empty schema + no schema history table",
        "symptom": "Found non-empty schema(s) but no schema history table 오류로 앱 시작 실패",
        "cause": "스키마는 남아 있는데 히스토리 테이블 삭제/rename",
        "fix": "새 DB로 시작하거나 baseline 전략을 명확히 적용",
        "prevention": "히스토리 테이블 수동 변경 금지, 환경별 Flyway 전략 명시",
    },
    {
        "title": "5. Java BOM(\\ufeff) 컴파일 오류",
        "symptom": "illegal character: '\\ufeff' / ?package ... 컴파일 오류",
        "cause": "Java 소스 파일이 UTF-8 BOM으로 저장됨",
        "fix": "문제 파일들을 UTF-8 무BOM으로 변환",
        "prevention": "에디터 기본 저장 형식을 UTF-8(no BOM)으로 통일",
    },
    {
        "title": "6. 인코딩 형식 문제 vs 문자열 자체 깨짐 구분",
        "symptom": "코드/화면에 ?? 또는 깨진 한글 표시",
        "cause": "일부는 BOM 문제, 일부는 깨진 문자열 literal이 이미 저장된 상태",
        "fix": "인코딩 포맷 정리 + 깨진 문자열 literal 직접 복구",
        "prevention": "일괄 수정 후 build/lint/화면 검증을 함께 수행",
    },
    {
        "title": "7. 금감원 API 금리 파싱 오류 (A/B/C/D)",
        "symptom": "0.12, 음수 금리 등 비현실적인 금리 값이 노출됨",
        "cause": "동일 fin_prdt_cd의 A/B/C/D 금리 유형을 개별 상품처럼 처리",
        "fix": "fin_prdt_cd 기준 그룹핑, A(대출금리) 우선, 없으면 B+C-D 계산",
        "prevention": "외부 API 필드 의미/매핑 규칙 문서화 및 이상값 탐지 규칙 추가",
    },
    {
        "title": "8. 금리 표시 규칙(음수/0 이하) 정리",
        "symptom": "음수 금리 또는 0 이하 금리가 UI에 그대로 표시됨",
        "cause": "계산값과 표시값 규칙 분리 부족",
        "fix": "음수 금리 보정 및 0 이하 금리 표시 규칙(공란/문구) 적용",
        "prevention": "계산 로직과 UI 표시 포맷 규칙을 분리 유지",
    },
    {
        "title": "9. DSR 초과인데 적합도 점수 높음",
        "symptom": "DSR 초과 경고와 높은 적합도 점수가 동시에 노출됨",
        "cause": "정책 위반/제외 판단과 점수 계산이 분리되어 패널티 반영 부족",
        "fix": "DSR 초과 시 점수 페널티 강화 및 제외 사유 UI 노출 정리",
        "prevention": "정책 위반과 점수 정합성 테스트케이스 유지",
    },
    {
        "title": "10. 추천 제외 상품/전체 상품 노출 누락",
        "symptom": "제외 상품이 없다고 뜨거나 전체 상품 수가 기대보다 적음",
        "cause": "사유 문자열 매칭과 프론트 분류/필터 로직이 혼합됨",
        "fix": "추천/제외 분리 기준 정리, 전체 상품을 모두 노출하도록 UI 재구성",
        "prevention": "API 응답 count와 화면 노출 count 비교 검증 추가",
    },
    {
        "title": "11. Provider URL 팝업에 URL 미노출",
        "symptom": "DB에 PROVIDER_URL 등록 후에도 팝업에 URL이 없음",
        "cause": "fin_co_no 매핑 불일치, 인증/프록시 문제, mapper/service 연결 이슈 가능",
        "fix": "LOAN_PRODUCT.fin_co_no와 PROVIDER_URL.fin_co_no 대조 + 인증 포함 API 응답 확인",
        "prevention": "상품별 fin_co_no 점검 SQL/응답 검증 절차 문서화",
    },
    {
        "title": "12. BFF 프록시 405/500 오류",
        "symptom": "/api/users/me/consents -> 405, /api/health -> 500",
        "cause": "GET 핸들러 미구현, 헬스체크 백엔드 경로 불일치",
        "fix": "BFF route GET 핸들러 추가, /actuator/health 경로로 수정",
        "prevention": "프록시 라우트 메서드 계약표/스모크 테스트 유지",
    },
    {
        "title": "13. LV2/LV3 저장 실패가 추천 전체 실패로 전파",
        "symptom": "선택 입력(LV2/LV3) 저장 실패만으로 추천 실행 전체 중단",
        "cause": "직렬 await + 공통 catch로 실패 전파",
        "fix": "LV2/LV3 저장을 개별 try/catch 처리하고 LV1 기반 추천 계속 진행",
        "prevention": "필수 입력/선택 입력 실패 처리 정책을 분리",
    },
    {
        "title": "14. LV1만 입력 시 동의 저장 실패",
        "symptom": "동의 체크 후에도 추천 실행 실패",
        "cause": "동의 저장 로직이 LV2/LV3 입력 조건에 묶여 있었음",
        "fix": "LV1만 있어도 동의 저장 수행, 동의 레벨 타입 확장",
        "prevention": "추천 선행조건(LV1/동의) 중심 테스트케이스 유지",
    },
    {
        "title": "15. 로그인 실패 횟수 5 이상 누적 안 됨",
        "symptom": "계정 잠금 후 FAIL_LOGIN_COUNT가 5에서 멈춤",
        "cause": "잠금 상태 증분 로직 미반영 또는 STS bin/main 구버전 클래스 실행",
        "fix": "잠금 상태에서도 increment 수행 + STS Clean/Rebuild 후 재시작",
        "prevention": "STS bin vs Gradle build 혼선 방지, 실행 기준 통일",
    },
    {
        "title": "16. 숫자 입력칸에 -, e 입력 가능",
        "symptom": "금액/나이 입력칸에 -, +, e, . 입력 가능",
        "cause": "HTML number input 기본 동작",
        "fix": "프론트 입력 차단/숫자 sanitize + 백엔드 @PositiveOrZero 검증 추가",
        "prevention": "UI validation + API validation 이중 적용 유지",
    },
    {
        "title": "17. 비밀번호 저장 보안(해시 적용)",
        "symptom": "비밀번호 평문/레거시 저장 가능성",
        "cause": "초기 구현에서 해시 저장 강제 부족",
        "fix": "BCrypt 해시 저장 적용, 로그인 시 BCrypt 검증, 레거시 plain 호환 유지",
        "prevention": "신규 가입 해시 저장 강제 및 레거시 계정 점진 마이그레이션 계획 수립",
    },
]


def _rt(text: str) -> list[dict]:
    return [{"type": "text", "text": {"content": text}}]


def _heading(level: int, text: str) -> dict:
    block_type = f"heading_{level}"
    return {"object": "block", "type": block_type, block_type: {"rich_text": _rt(text)}}


def _paragraph(text: str) -> dict:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": _rt(text)}}


def _bullet(text: str) -> dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": _rt(text)},
    }


def build_troubleshooting_blocks() -> list[dict]:
    blocks: list[dict] = [
        _heading(1, "LOAN WISELY 프로젝트 트러블슈팅 가이드 (1~17)"),
        _paragraph("프로젝트 진행 중 실제로 발생한 이슈를 증상/원인/해결/재발 방지 기준으로 정리한 문서입니다."),
        _paragraph("범위: 기존 정리 항목 중 1번부터 17번까지. (18번 이후 lint/Notion 이슈 제외)"),
    ]
    for item in TROUBLESHOOTING_ITEMS:
        blocks.append(_heading(2, item["title"]))
        blocks.append(_bullet(f"증상: {item['symptom']}"))
        blocks.append(_bullet(f"원인: {item['cause']}"))
        blocks.append(_bullet(f"해결: {item['fix']}"))
        blocks.append(_bullet(f"재발 방지: {item['prevention']}"))
    return blocks


def build_troubleshooting_detailed_blocks() -> list[dict]:
    sections: list[tuple[str, list[tuple[str, str, str, str, str, str]]]] = [
        (
            "Flyway / Oracle ??????",
            [
                (
                    "1. Flyway ?? validate ?? ? half-completed migration",
                    "? ?? ? Validate failed / failed migration ???? ApplicationContext ?? ??",
                    "?????? ?? ?? ??? ??? ??(flyway_schema_history)? ?? ?? ??? ???? ??",
                    "?? ?? ?? ?? ???? ??, ??/??? ??? ?? ????. ?????? ? DB ?? baseline ?? ???????? ?????.",
                    "Spring Boot ?? ??, Flyway validate ???, flyway_schema_history ?? ??",
                    "?? ??? ?? ?? ???, ?? ? DB ?? ???? ?? ??",
                ),
                (
                    "2. flywayRepair Gradle task ??? ??",
                    "./gradlew flywayRepair ?? ? Task not found",
                    "?? ????? Spring Boot Auto Flyway ?? ???? Flyway Gradle plugin task? ???? ??",
                    "Gradle task ?? ?? Spring/Flyway ?? ?? ???? ?? ??? ????. ?? ? plugin? ?? ????.",
                    "build.gradle ??? gradle tasks ?? ??",
                    "Flyway ?? ??(Spring Auto/Gradle plugin) ?? ?? ???",
                ),
                (
                    "3. Oracle quoted identifier / ???? ?? (FLYWAY_SCHEMA_HISTORY)",
                    "???/?? ?? ? ORA-00904, ORA-00942? ??? ??",
                    "Oracle?? quoted ???(???)? unquoted(???) ?? ??? ???? ?? rename/?? ??",
                    "Flyway? ??? schema history ??? ???? ????, ?? rename/?? ??? ????. ? DB??? Flyway? ???? ?????? ????.",
                    "user_tables / user_tab_columns ??, Flyway? ????? SQL ??",
                    "FLYWAY_SCHEMA_HISTORY ?? rename/?? ?? ??",
                ),
                (
                    "4. non-empty schema but no schema history table",
                    "????? ??? ????? Flyway? schema history table? ?? ?? ?? ??",
                    "?? ?? ???? history table? ??/rename??? Flyway ?? ??? ???",
                    "? ???(?? ? DB)? ????? baseline ??????? ????. ??? baselineOnMigrate ??? ???? ?? ??? ?? ????.",
                    "Flyway startup ??? ?? ??? ?? ? ??",
                    "??? Flyway baseline ??? ??? ???",
                ),
                (
                    "5. ORA-00904: installed_rank invalid identifier",
                    "Flyway? schema history ?? ? installed_rank ?? ??? ??",
                    "?? ??/??? FLYWAY_SCHEMA_HISTORY ?? ??? Flyway ??? ???? ???? ???",
                    "Flyway ?? ???? history ???? ?????. ?????? ? DB/? ??? ??? ?? ????.",
                    "user_tab_columns?? installed_rank ?? ??? ?? ?? ??",
                    "history ???? ?????? ??? ?? ???? ??",
                ),
                (
                    "6. ?????? ?? ??? ?? ? ?? ?? ??",
                    "? DB ?? ? ?????? ?? ?? ?? ??/?? ??? ??",
                    "?? ??/?? ? Flyway ??? ????? ?? ?? ?? bootstrap ??? ??",
                    "?? V1~V23? ? DB ?? ?? baseline SQL? ??(squash)?? legacy ??? ?? ?? ??? ??",
                    "migration ??? legacy ?? ?? ??, ? DB ?? ??",
                    "? DB ?? baseline ??? ?? ?? DB ?? ??",
                ),
            ],
        ),
        (
            "DB ?? / ??? ??? ???",
            [
                (
                    "7. ??? ?? ?? ?? ?? ? ?????? ???? ?? ??",
                    "??? ?? ?? ?? ?? ?? ?????? ??? Flyway ??? ?? ??",
                    "V22 ? ? ?? Flyway ??? ???? ??? ???? ???? ??",
                    "?? Flyway ?? ??? ??? ? USER_AUTH ?? ??? ????. ?????? ??? ??? ?? ??? ????.",
                    "? ?? ?? ??, USER_AUTH ?? ??/??? ??, ??? API ??",
                    "?? ?? ?? ?????? ?? ??? ?? ??",
                ),
                (
                    "8. ?? ?? ?? (LV1? ??? ??)",
                    "LV1 ?? + ?? ?? ? ?? ?? ? ?? ?? ??? ?? ?? ??",
                    "????? ?? ?? ??? LV2/LV3 ?? ?? ??? ?? ???",
                    "LV1? ??? ?? ?? API? ????? useRecommendFlow ??? ???? ?? ?? ??? 1 ???? ????.",
                    "???? Network?? /api/users/me/consents ?? ??? ?? ?? ??",
                    "?? ??(LV1, ??)? ?? ??(LV2/LV3) ?? ?? ??",
                ),
                (
                    "9. LV2/LV3 ?? ??? ?? ?? ??? ??",
                    "?? ?? ?? API ?? ???? ?? ?? ??? ?? ???? ??",
                    "useRecommendFlow?? LV2/LV3 ??? ?? await + ?? catch? ??",
                    "LV2/LV3 ??? ?? try/catch? ??? ?? ? ?? ??? ???? LV1 ?? ??? ?? ????.",
                    "LV2/LV3 ?? ??? /api/recommendations ??? ????? ??",
                    "?? ?? ??? degrade ???? ?? ??? ??",
                ),
                (
                    "10. ??? ?? ?? 5? ?? ???? ??",
                    "?? ?? ???? ??? ??? ????? FAIL_LOGIN_COUNT? 5?? ??",
                    "?? ???? incrementFailLoginCount ?? ?? ??? ????? STS? ??? bin/main ???? ??",
                    "?? ????? fail_login_count? ?????? ??? ?? ? STS Clean/Rebuild ? ?? ????? ?? ??? ????.",
                    "USER_AUTH.fail_login_count ?? SQL, Spring ??, ?? ??? ?? ??",
                    "STS/Gradle ?? ?? ?? ?? ? ??? ?? ???",
                ),
                (
                    "11. Provider URL ???? URL ???",
                    "DB? PROVIDER_URL? ??? ?? ?? ????? URL? null/????? ??",
                    "LOAN_PRODUCT.fin_co_no? PROVIDER_URL.fin_co_no ???, ?? ?? ??? API ??, ?? mapper/service ?? ??",
                    "??? fin_co_no ????? PROVIDER_URL ?? ???? SQL? ????, ?? ??? ?? ?? API ??(providerUrl) ??? ????.",
                    "LOAN_PRODUCT / PROVIDER_URL ?? SQL, ???? Network ?? JSON(providerUrl)",
                    "fin_co_no ?? ?? SQL? ?? ?????? ??",
                ),
                (
                    "12. ???? ?? ?? ???? ?? ?? ??? ??",
                    "??? ? ??? TC_* ??? ?? ?? ?? ?? ??? ??",
                    "????? ?? ???? ??/?? ??? ?? LOAN_PRODUCT? ???? ???? ??",
                    "??? ??(prefix) ???? ?? ???? ?? ?? ? COMMIT??, ?? ? ?? ?? ????? ????.",
                    "LOAN_PRODUCT?? product_name LIKE 'TC_%' ??",
                    "??? ??? ??? ??? ?? ?? ???",
                ),
            ],
        ),
        (
            "?? API ?? ?? / ?? ??",
            [
                (
                    "13. ??? API ?? 0.12 / ?? ?? ??",
                    "???? ????? 0.12 ?? -0.15?? ????? ??? ??",
                    "?? ??(fin_prdt_cd)? A/B/C/D ??? ?? ?? ?? ??? ????? ?? ??? ??",
                    "fin_prdt_cd ???? ??? ????? A(????) ?? ??, A? ??? B+C-D ?? ??? ????.",
                    "??? ?? ??? ? ?? ?? ??? fin_prdt_cd ??? ??",
                    "?? API ?? ??/????(A/B/C/D) ??? ? ???? ?? ?? ??",
                ),
                (
                    "14. ?? ?? ??(0 ?? ? ??) ???",
                    "?? ???? ??/0 ?? ?? ??? ?? ??",
                    "???? UI ??? ??? ???? ?? ????? ??? ??? ???",
                    "?? ??? ?? ??? ????, 0 ?? ??? ??/??/?? ?? ??? ???? ??? ????.",
                    "?? ??/?? ???/?? ?? ??? ?? ??? ??",
                    "?? ?? ??? ?? ???? ?? ??",
                ),
            ],
        ),
        (
            "??? / ?? / ?? ??",
            [
                (
                    "15. Java BOM(\ufeff)? compileJava ??",
                    "compileJava?? illegal character: \ufeff ? ?package ?? ?? ??",
                    "?? Java ??? UTF-8 BOM?? ???? javac? BOM? ??? ??",
                    "?? ??? UTF-8 ?BOM?? ???? ??????.",
                    "Gradle compileJava ??, ?? ? ???(BOM) ??",
                    "??? ?? ?? ???? UTF-8(no BOM)?? ??",
                ),
                (
                    "16. ??? ?? ??? ?? ??? literal ??",
                    "??/??? ?? ?? ?? ??? ????",
                    "??? ?? ??? ?? ???? ??? ?? ?? ???? ??? ??? ??",
                    "UTF-8 ?? ?? ??? ?? ???? literal ??? ?? ???? lint/build? ?? ???? ????.",
                    "UTF-8/BOM ?? ??? ?? ?? ??? ??",
                    "??? ??? ??? ?? ??? ?? ??? ??",
                ),
                (
                    "17. STS/Eclipse bin/main ? Gradle build/classes ??",
                    "??? ??? ???? ?? ??? ???? ?? ??? ?? ??",
                    "STS ??? bin/main?, Gradle compileJava? build/classes? ???? ?? ??? ???",
                    "Project Clean/Rebuild ? STS ?? ??? ?? ?? ??? Gradle ???? ?????.",
                    "??? ??? ??, ?? ?? ?? ??, ??/?? ?? ??",
                    "? ?? ??(STS/Gradle)? ??? ?? ???",
                ),
            ],
        ),
    ]

    blocks: list[dict] = [
        _heading(1, "LOAN WISELY ????? ??? (??? ? ???????)"),
        _paragraph("???? ?? ? ??? ??? ?? ? ??? ??? ?? ??/FAIL ?? ??? ????, ????? ???? ?? ???? ?? ??? ?? ?? ???? ??? ?????."),
        _paragraph("??: Flyway/Oracle, DB ??/???, ?? API ?? ??, ???/??/????. (??? ??? ID ?? ?? ??? ??)"),
    ]

    for section_title, items in sections:
        blocks.append(_heading(2, section_title))
        for title, symptom, cause, fix, verify, prevention in items:
            blocks.append(_heading(3, title))
            blocks.append(_bullet(f"??: {symptom}"))
            blocks.append(_bullet(f"??: {cause}"))
            blocks.append(_bullet(f"??: {fix}"))
            blocks.append(_bullet(f"?? ???: {verify}"))
            blocks.append(_bullet(f"?? ??: {prevention}"))
    return blocks


def build_troubleshooting_detailed_blocks_v2() -> list[dict]:
    sections: list[tuple[str, list[tuple[str, str, str, str, str]]]] = [
        (
            "Flyway / Oracle / 마이그레이션",
            [
                (
                    "1. Flyway validate 실패 (half-completed migration)",
                    "앱 기동 시 Validate failed / failed migration 메시지로 ApplicationContext가 올라오지 않음",
                    "마이그레이션 중간 실패 상태가 flyway_schema_history와 실제 DB 객체 상태에 불일치로 남음",
                    "실패 이력만 수동으로 건드리지 않고 이력+스키마 상태를 함께 정리. 최종적으로 새 DB 기준 baseline 통합 마이그레이션으로 재정렬",
                    "flyway_schema_history 직접 수정 최소화, 실패 시 DB 객체 상태까지 함께 점검",
                ),
                (
                    "2. flywayRepair Gradle task 미존재",
                    "./gradlew flywayRepair 실행 시 Task not found",
                    "프로젝트가 Spring Boot Auto Flyway 중심이라 Flyway Gradle plugin task가 등록되지 않음",
                    "Gradle task 대신 Spring/Flyway 자동 실행 기준으로 복구 절차 수행. 필요 시 plugin을 별도 추가",
                    "Flyway 운영 방식(Spring Auto / Gradle plugin) 문서화",
                ),
                (
                    "3. Oracle 대소문자/quoted identifier 혼선",
                    "ORA-00904, ORA-00942가 번갈아 발생하면서 history table 조회가 불안정함",
                    "Oracle의 quoted/unquoted 식별자 규칙을 무시하고 수동 rename/조회 수행",
                    "Flyway가 생성한 history table 구조를 기준으로 유지하고 수동 rename/컬럼 변경 중단",
                    "FLYWAY_SCHEMA_HISTORY 수동 rename/컬럼 변경 금지",
                ),
                (
                    "4. non-empty schema but no schema history table",
                    "스키마에는 객체가 있는데 Flyway가 schema history table을 찾지 못해 기동 실패",
                    "history table 삭제/rename 또는 기대 구조 불일치",
                    "새 스키마(또는 새 DB)에서 baseline 적용. 임시로 baselineOnMigrate 전략 검토 가능",
                    "환경별 Flyway baseline 전략 사전 정의",
                ),
                (
                    "5. ORA-00904: installed_rank invalid identifier",
                    "Flyway가 history table 조회 중 installed_rank 컬럼 에러로 실패",
                    "수동 생성/변경된 FLYWAY_SCHEMA_HISTORY 구조가 Flyway 버전 기대 스키마와 다름",
                    "Flyway 표준 schema history 구조로 재정렬(실질적으로 새 DB/새 스키마가 가장 안전)",
                    "history table은 애플리케이션/Flyway가 관리하도록 유지",
                ),
                (
                    "6. FLYWAY_SCHEMA_HISTORY 수동 rename 이후 추가 오류 연쇄",
                    "한 오류를 막으려 수동으로 테이블명/컬럼명을 바꾼 뒤 다른 오류가 계속 발생",
                    "Flyway 메타테이블을 운영 데이터 테이블처럼 직접 수정하면서 기대 스키마가 더 멀어짐",
                    "수동 수정 중단 후 새 DB 기준으로 재기동 절차 재설계",
                    "메타테이블 수동 변경 금지 원칙 유지",
                ),
                (
                    "7. 마이그레이션 파일 과다로 신규 환경 부팅 부담",
                    "신규 DB 연결 시 Flyway 파일 수가 많아 검증/관리 복잡도 증가",
                    "기능 추가 과정에서 마이그레이션 파일이 누적됨",
                    "V1~V23을 새 DB 기준 단일 baseline SQL로 통합(squash)하고 legacy 파일은 보관 폴더로 이동",
                    "신규 환경용 baseline 정책과 기존 운영 DB 정책 분리",
                ),
            ],
        ),
        (
            "DB 저장 / 추천 흐름 / 사용자 데이터",
            [
                (
                    "8. 로그인 실패 저장 기능 검증 전에 Flyway 오류로 앱 기동 불가",
                    "로그인 실패 횟수 저장 로직을 보려 해도 앱이 먼저 기동 실패",
                    "USER_AUTH 관련 로직 문제가 아니라 선행 Flyway 오류가 원인",
                    "마이그레이션 성공 상태를 먼저 확보한 뒤 로그인 실패 저장 로직을 검증",
                    "기능 검증 전 선행 인프라(Flyway/DB) 상태 확인",
                ),
                (
                    "9. 동의 저장 실패 (LV1만 입력 시)",
                    "LV1 입력 + 동의 체크 후 추천 실행 시 동의 저장 실패로 전체 흐름 중단",
                    "동의 저장 호출이 LV2/LV3 입력 조건에 묶여 있었음",
                    "LV1만 있어도 동의 저장 API를 호출하도록 프론트 흐름 수정",
                    "필수 단계(LV1/동의)와 선택 단계(LV2/LV3) 로직 분리",
                ),
                (
                    "10. LV2/LV3 저장 실패가 추천 전체 실패로 전파",
                    "선택 정보 저장 API 하나 실패하면 추천 실행 전체가 실패 알림으로 종료",
                    "LV2/LV3 저장이 직렬 await + 공통 catch로 처리됨",
                    "LV2/LV3 저장은 개별 try/catch로 격리하고 LV1 기반 추천은 계속 수행",
                    "선택 입력 실패는 degrade 처리 패턴 유지",
                ),
                (
                    "11. LV1 미입력 / 동의 미체크 상태에서 추천 실행 차단 필요",
                    "UI 또는 API 우회로 추천이 실행될 가능성이 있었음",
                    "프론트 차단만으로는 백엔드 직접 호출을 막을 수 없음",
                    "프론트 입력 검증 + 백엔드 추천 생성 API에서 LV1/동의 강제 검증 추가",
                    "정책성 제약은 항상 백엔드에서 최종 강제",
                ),
                (
                    "12. 로그인 실패 횟수 5회 이후 증가하지 않음",
                    "계정 잠금 후에도 FAIL_LOGIN_COUNT가 5에서 멈춤",
                    "잠금 분기에서 increment 호출 없이 예외 반환 또는 구버전 클래스 실행",
                    "잠금 상태에서도 fail_login_count 증가하도록 서비스 수정 + 재빌드/재시작",
                    "STS bin/main vs Gradle build/classes 실행 혼선 주의",
                ),
                (
                    "13. Provider URL 팝오버에 URL 미노출",
                    "DB에 URL을 넣었는데 팝오버에는 등록된 URL 없음으로 표시",
                    "fin_co_no 불일치, 인증 없는 상태로 API 확인, mapper/service 연결 문제 등이 복합 원인",
                    "LOAN_PRODUCT.fin_co_no와 PROVIDER_URL.fin_co_no를 SQL로 대조하고 인증 상태에서 API 응답(providerUrl) 확인",
                    "상품/기관 코드 매핑 점검 SQL을 운영 체크리스트화",
                ),
                (
                    "14. 테스트 생성 더미 데이터가 실조회 화면에 노출",
                    "TC_* 테스트 상품이 전체 금융 상품 조회 화면에 보임",
                    "테스트 데이터와 운영성 조회 데이터가 같은 테이블을 사용하고 정리 누락",
                    "패턴(prefix) 기반 더미 데이터 정리 SQL로 삭제 후 COMMIT",
                    "테스트 데이터 명명 규칙과 자동 정리 절차 마련",
                ),
            ],
        ),
        (
            "외부 API 금리 파싱 / 표시 규칙",
            [
                (
                    "15. 금감원 API A/B/C/D 옵션을 상품별 금리로 오해",
                    "같은 상품인데 금리 값이 비정상적으로 낮거나 음수로 보임",
                    "fin_prdt_cd 단위 옵션(A/B/C/D)을 독립 상품처럼 처리",
                    "fin_prdt_cd 기준 그룹핑 후 A(대출금리) 우선, A 없으면 B+C-D 계산",
                    "외부 API 필드 의미와 매핑 규칙 문서화",
                ),
                (
                    "16. 금리 0.12 / -0.15 같은 비현실 값 노출",
                    "신용대출 금리가 0.x% 또는 음수로 표시",
                    "필드 의미 오해/스케일 오해 또는 가산/조정금리 조합 처리 미흡",
                    "A 우선 규칙 적용 및 계산값 보정 로직으로 비정상값 노출 방지",
                    "원본 API 응답과 화면 표시값 교차검증 절차 유지",
                ),
                (
                    "17. 금리 표시 정책이 화면마다 불일치",
                    "어떤 화면은 음수/0 이하를 그대로 보여주고, 어떤 화면은 문구로 표시",
                    "계산값과 표시값 정책이 분리되지 않음",
                    "계산 로직과 표시 포맷터를 분리하고 화면 정책(공란/문구/범위)을 명확화",
                    "금리 표시 규칙을 공통 함수로 관리",
                ),
            ],
        ),
        (
            "인코딩 / 빌드 / 실행 환경 / 도구",
            [
                (
                    "18. Java BOM(\\ufeff)로 compileJava 실패",
                    "illegal character: \\ufeff, ?package 형태 컴파일 오류 발생",
                    "일부 Java 파일이 UTF-8 BOM으로 저장됨",
                    "문제 파일을 UTF-8 무BOM으로 변환 후 재컴파일",
                    "에디터 저장 인코딩 UTF-8(no BOM) 통일",
                ),
                (
                    "19. 인코딩 형식 문제와 문자열 literal 깨짐 혼재",
                    "화면/코드에 ?? 또는 깨진 한글이 남음",
                    "일부는 인코딩 포맷(BOM) 문제, 일부는 이미 깨진 문자열이 소스에 저장된 상태",
                    "UTF-8 형식 정리 후 literal 자체를 수동 복구, lint/build로 재검증",
                    "인코딩 정리와 내용 복구를 별도 단계로 처리",
                ),
                (
                    "20. STS/Eclipse bin/main vs Gradle build/classes 혼선",
                    "수정했는데 동작이 예전과 같아 보임",
                    "STS 실행은 bin/main, Gradle compileJava는 build/classes를 갱신",
                    "Project Clean/Rebuild 후 STS 재시작 또는 실행 기준을 Gradle 중심으로 통일",
                    "실행 도구/출력 경로 표준화",
                ),
                (
                    "21. Windows lock 파일(checksum.lock) 복사 실패",
                    "파일 복사 중 0x80070021 / checksum.lock 잠금 오류 발생",
                    "Gradle/IDE/서버가 lock 파일을 사용 중",
                    "프로세스 종료 후 복사하거나 생성물/lock 파일은 복사 대상에서 제외",
                    "백업/복사 대상에서 .gradle, build, .next, node_modules 제외",
                ),
            ],
        ),
        (
            "Notion 자동화 운영 이슈 (테스트 케이스 이력 제외)",
            [
                (
                    "22. Public API 통합 화면에서 Internal 통합 생성 시도",
                    "Internal 옵션이 안 보이고 공개용 필수 항목(회사명/웹사이트 등)만 보임",
                    "Notion의 public integrations 화면으로 들어감",
                    "Internal integrations 메뉴에서 내부 통합 생성",
                    "목적이 내부 자동화면 항상 Internal integration 사용",
                ),
                (
                    "23. Notion parent_page_id validation_error",
                    "page_id should be a valid uuid 오류",
                    "슬러그 포함 값(CCKSY-<id>) 또는 URL 전체를 그대로 전달",
                    "32자리 ID/UUID만 사용하거나 스크립트에서 page_id 정규화 처리",
                    "환경변수 저장 시 page_id 형식 검증",
                ),
                (
                    "24. Notion DB 생성 시 Status property 스키마 오류",
                    "status.options should be not present 오류로 DB 생성 실패",
                    "Notion API가 status 타입 생성 시 options 지정에 제한이 있음",
                    "Status 컬럼을 status 대신 select 타입으로 정의",
                    "Notion API 스키마 제약 기준으로 템플릿 설계",
                ),
                (
                    "25. Notion page create children 100개 제한 초과",
                    "상세 트러블슈팅 페이지 생성 시 children.length > 100 validation_error",
                    "한 번의 create_page 요청에 블록을 100개 초과로 전달",
                    "페이지 생성을 100개 단위로 chunking(create_page + append_block_children) 처리",
                    "긴 문서는 항상 chunk append 전략 사용",
                ),
                (
                    "26. Notion 토큰 노출 위험",
                    "콘솔/채팅 공유 중 토큰 문자열이 외부에 노출됨",
                    "토큰을 평문으로 붙여넣는 운영 습관",
                    "즉시 토큰 회전(revoke/재발급) 후 환경변수로만 사용",
                    "토큰은 스크립트/문서/채팅에 직접 기록하지 않기",
                ),
            ],
        ),
    ]

    blocks: list[dict] = [
        _heading(1, "LOAN WISELY 트러블슈팅 가이드 (상세판 · 비테스트케이스)"),
        _paragraph("프로젝트 진행 중 실제로 발생한 이슈 중 테스트 케이스 FAIL/PASS 이력 자체를 제외하고, 운영·개발 관점에서 재발 가능성이 높은 문제를 상세 절차 중심으로 정리한 문서입니다."),
        _paragraph("범위: Flyway/Oracle, DB 저장/정합성, 외부 API 금리 파싱, 인코딩/빌드/실행환경, Notion 자동화 운영 이슈"),
    ]
    for section_title, items in sections:
        blocks.append(_heading(2, section_title))
        for title, symptom, cause, action, prevention in items:
            blocks.append(_heading(3, title))
            blocks.append(_bullet(f"증상: {symptom}"))
            blocks.append(_bullet(f"원인: {cause}"))
            blocks.append(_bullet(f"조치: {action}"))
            blocks.append(_bullet(f"재발 방지: {prevention}"))
    return blocks


def normalize_notion_id(raw: str) -> str:
    value = (raw or "").strip()
    if not value:
        return ""

    compact = re.sub(r"[^0-9a-fA-F]", "", value)
    match = re.search(r"([0-9a-fA-F]{32})", compact)
    if match:
        hex_id = match.group(1).lower()
        return f"{hex_id[0:8]}-{hex_id[8:12]}-{hex_id[12:16]}-{hex_id[16:20]}-{hex_id[20:32]}"

    uuid_match = re.search(
        r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})",
        value,
    )
    if uuid_match:
        return uuid_match.group(1).lower()

    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create Notion pages/databases for LOAN WISELY docs/templates via Notion API."
    )
    parser.add_argument(
        "--parent-page-id",
        default=os.getenv("NOTION_PARENT_PAGE_ID", "").strip(),
        help="Target parent page ID in Notion (or set NOTION_PARENT_PAGE_ID)",
    )
    parser.add_argument(
        "--mode",
        choices=["hub-page", "test-db", "troubleshooting-page", "troubleshooting-page-detailed", "all"],
        default="all",
        help="Which template(s) to create",
    )
    parser.add_argument(
        "--prefix",
        default="LOAN WISELY",
        help="Prefix used in generated page/database titles",
    )
    return parser.parse_args()




def create_page_chunked(client: NotionClient, parent_page_id: str, title: str, children: list[dict] | None = None) -> dict:
    all_children = list(children or [])
    first_chunk = all_children[:100]
    page = client.create_page(parent_page_id=parent_page_id, title=title, children=first_chunk or None)
    if len(all_children) <= 100:
        return page

    page_id = page.get("id")
    if not page_id:
        raise RuntimeError("Notion page id missing after page creation")

    for i in range(100, len(all_children), 100):
        client.append_block_children(page_id, all_children[i:i + 100])
    return page


def create_hub_page(client: NotionClient, parent_page_id: str, prefix: str) -> dict:
    title = f"{prefix} 운영 허브"
    blocks = load_json_file(str(TEMPLATE_DIR / "hub_page_children.json"))
    return client.create_page(parent_page_id=parent_page_id, title=title, children=blocks)


def create_test_scenario_db(client: NotionClient, parent_page_id: str, prefix: str) -> dict:
    title = f"{prefix} 테스트 시나리오"
    properties = load_json_file(str(TEMPLATE_DIR / "test_scenario_db_properties.json"))
    return client.create_database(parent_page_id=parent_page_id, title=title, properties=properties)


def create_troubleshooting_page(client: NotionClient, parent_page_id: str, prefix: str) -> dict:
    title = f"{prefix} 트러블슈팅 가이드 (1~17)"
    return create_page_chunked(client, parent_page_id=parent_page_id, title=title, children=build_troubleshooting_blocks())

def create_troubleshooting_detailed_page(client: NotionClient, parent_page_id: str, prefix: str) -> dict:
    title = f"{prefix} 트러블슈팅 가이드 (상세판 · 비테스트케이스)"
    return create_page_chunked(client, parent_page_id=parent_page_id, title=title, children=build_troubleshooting_detailed_blocks_v2())


def main() -> None:
    args = parse_args()
    if not args.parent_page_id:
        raise SystemExit("Missing parent page id. Use --parent-page-id or set NOTION_PARENT_PAGE_ID.")

    args.parent_page_id = normalize_notion_id(args.parent_page_id)

    client = NotionClient.from_env()

    results: list[tuple[str, str, str]] = []

    if args.mode in ("hub-page", "all"):
        hub = create_hub_page(client, args.parent_page_id, args.prefix)
        results.append(("hub-page", hub.get("id", ""), hub.get("url", "")))

    if args.mode in ("test-db", "all"):
        db = create_test_scenario_db(client, args.parent_page_id, args.prefix)
        results.append(("test-db", db.get("id", ""), db.get("url", "")))

    if args.mode in ("troubleshooting-page", "all"):
        page = create_troubleshooting_page(client, args.parent_page_id, args.prefix)
        results.append(("troubleshooting-page", page.get("id", ""), page.get("url", "")))

    if args.mode in ("troubleshooting-page-detailed", "all"):
        page = create_troubleshooting_detailed_page(client, args.parent_page_id, args.prefix)
        results.append(("troubleshooting-page-detailed", page.get("id", ""), page.get("url", "")))

    print("Created Notion templates:")
    for kind, object_id, url in results:
        print(f"- {kind}: id={object_id} url={url}")


if __name__ == "__main__":
    main()
