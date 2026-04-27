# 문서 및 증거 정책

## 적용 대상
- `docs/ai/**`
- `.claude/**` (규칙/정책 문서)
- `tests/evidence/**`

## 목표 규칙

### 갱신 트리거

| 변경 종류 | 갱신 대상 |
|---|---|
| 기능 추가/수정 | `docs/ai/CURRENT_STATE.md` |
| 테스트 수행 | `docs/ai/catalogs/TEST_HISTORY.md` + `tests/evidence/` |
| 구조/모듈 변경 | `docs/ai/catalogs/PROJECT_MAP.md` + fingerprint 갱신 |
| 컨벤션 위반 발견 | `docs/ai/catalogs/CONVENTION_DRIFT.md` |
| 보안 이슈 발견 | `docs/ai/policy/SECURITY_POLICY.md` |
| 다음 작업 식별 | `docs/ai/NEXT_ACTIONS.md` |
| 실패·반복 실수 | `docs/ai/catalogs/FAILURE_PATTERNS.md` (append-only) |
| Round 검증 | `tests/evidence/<날짜>-<vendor>.md` + `docs/19_decision-log.md` |
| 외부 시스템 계약 변경 | `docs/ai/catalogs/EXTERNAL_CONTRACTS.md` |
| 벤더 어댑터 추가 | `docs/ai/catalogs/VENDOR_ADAPTERS.md` + `.claude/ai-context/vendors/` |

### PROJECT_MAP fingerprint

- 구조 변경 → `python scripts/ai/check_project_map_drift.py --update`
- 세션 시작 hook이 자동 drift 체크
- **Forbidden**: 구조 변경만 하고 PROJECT_MAP/fingerprint 갱신 안 함

### 문서 작성 원칙

- 한국어 기본 (영어 기술 용어 병기 가능)
- 실제 결과만 기록 (추정은 추정이라고 명시)
- 절대 날짜 (YYYY-MM-DD) — 상대 날짜 금지
- 실무자 문서처럼 (마케팅 문구 금지)

### 문서 기준선 보호

- `CLAUDE.md`, `GUIDE_FOR_AI.md`, `REQUIREMENTS.md`, `README.md`, `docs/01~19`, `.claude/{rules,policy,skills,agents,ai-context,templates}/`는 실제 변경이 있을 때만 수정
- 설명 다듬기 용도의 수정 금지

---

## 문서 보존 판정 기준

### 근본 질문

> "다음 기능 개발 / 리팩토링 / 리뷰 / 디버깅 작업에서 **AI(Claude Code)가 이 문서를 참조하면 실제 도움이 되는가?**"

- YES → 남긴다 (active 위치)
- NO → 남기지 않는다 (삭제 또는 archive)

server-exporter는 내부 프로젝트. 규제 감사 대상 아님. 감사 증명용 이력은 git log + cycle log에 보존.

### 남기는 것 (AI 참조 가치)

| 유형 | 예시 |
|---|---|
| 현재 유효한 규칙 | `.claude/rules/*.md`, `.claude/policy/*.yaml` |
| 결정의 reasoning | `docs/ai/decisions/ADR-*.md` |
| 실행 패턴 사례 | `docs/ai/impact/*.md`, `handoff/*.md` |
| 현재 상태 스냅샷 | `CURRENT_STATE.md`, `PROJECT_MAP.md` |
| 알려진 이슈 | `CONVENTION_DRIFT.md`, `FAILURE_PATTERNS.md` |
| 외부 계약 노트 | `EXTERNAL_CONTRACTS.md` |
| Round 검증 결과 | `tests/evidence/` |
| 실측 매트릭스 | `VENDOR_ADAPTERS.md`, `JENKINS_PIPELINES.md` |

### 남기지 않는 것

| 패턴 | 대체 |
|---|---|
| 본문 cycle 번호 태그 | `harness/cycle-*-log.md` |
| 1회성 audit/review (정책 흡수된 것) | `docs/ai/archive/` 또는 삭제 |
| V1/V2/V3 parallel 버전 | 기존 파일 in-place 갱신 |

### 매 cycle 자문

> "이번 cycle에서 추가한 문서 중 '감사 증명용 이력'인 것은? → archive 또는 삭제."

### 금지 패턴

- V-number 증가 (V2 있으면 V3 새 파일 만들지 말고 V2 in-place)
- 본문 cycle 태그 박기
- 1회성 review를 같은 cycle에서 archive 안 옮김

---

## Archive 진입 기준

### Archive로 (역사 근거)

| 유형 | 예시 |
|---|---|
| 구조·정책 전환의 결정 이력 | `INITIAL_STATE_*.md` |
| 완결된 cycle 로그 (최신 N개 제외) | `cycle-001.md` ~ |
| Deprecated active 문서 과거본 | `FOO_V1.md` (V2가 active 일 때) |

### 물리 삭제 (git log에 맡기기)

| 유형 | 예시 |
|---|---|
| 1회성 빌드/배포 로그 | `BUILD_VERIFICATION_LOG.md` |
| 1회성 cleanup 보고서 | `ARTIFACT_CLEANUP_*.md` |
| PR description 복제본 | (PR에 이미 있음) |

### 판정 3 질문

1. "왜 지금 이 모습인지"를 설명하나? → archive
2. git log / cycle log에 이미 있나? → 삭제
3. 6개월 내 "이 파일 어디?" 물을 사람? → archive

## 금지 패턴

- 코드 변경 후 문서 갱신 누락
- 테스트 후 TEST_HISTORY 미기록
- 상대 날짜 ("어제", "지난주")
- 추정을 사실처럼

## 리뷰 포인트

- [ ] 코드 변경 PR이 CURRENT_STATE 갱신 포함
- [ ] 테스트 결과 TEST_HISTORY 기록
- [ ] PROJECT_MAP fingerprint 갱신 (구조 변경 시)

## 관련

- skill: `update-evidence-docs`, `measure-reality-snapshot`
- templates: `.claude/templates/CURRENT_STATE.template.md` 등
