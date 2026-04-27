# Commit 메시지 컨벤션

## 적용 대상
- 저장소 전체 (`**`)
- 모든 git commit (사람/AI 공통)

## 형식

```
<type>: <제목>

<본문 — 선택, 3줄 이내>
```

## type 목록 (고정)

| type | 용도 | 예시 |
|---|---|---|
| `feat` | 신규 기능 | `feat: Huawei vendor adapter 추가` |
| `fix` | 버그 수정 | `fix: callback URL 후행 슬래시 방어` |
| `refactor` | 기능 변경 없는 구조 개선 | `refactor: gather/normalize 책임 분리` |
| `docs` | 문서만 | `docs: docs/13 Round 11 추가` |
| `test` | 테스트 추가/수정 | `test: HPE iLO6 baseline 추가` |
| `chore` | 빌드/의존성/설정 | `chore: requirements.yml 갱신` |
| `harness` | AI 하네스 변경 | `harness: rule 22 fragment-philosophy 보강` |
| `hotfix` | 운영 긴급 수정 | `hotfix: Jenkins Stage 4 timeout 60s` |

이 목록 외 type 사용 금지.

## 제목 규칙

- **50자 hard limit**
- 한국어/영어 혼용 가능. 기술 용어는 영문 (`redfish_gather.py`, `iDRAC9`)
- 끝에 마침표 없음
- **무엇을/왜** 명시. 모호한 단어 단독 금지
- 티켓 있는 변경: `feat: [SUB-1] DAY_1 enum 확장` (선택)

## 금지어 (단독 사용 금지)

다음이 제목 **subject 전부**:
- `버그수정`, `수정`, `변경`, `업데이트`, `작업`
- `fix`, `update`, `change` (subject 단독)
- `WIP`, `wip`, `임시`, `test` (subject 단독)

다른 단어와 함께 쓰면 허용. 예: `fix: 빌링 합계 오산 수정` ✓ / `fix: 수정` ✗

## 본문 규칙

- **3줄 이내** (hard limit)
- **why > what** (코드만 봐도 알 수 있는 "무엇" 보다 "왜")
- 관련 티켓: `Ticket: docs/...` 또는 `Refs: ...`
- 4줄 이상 시 hook 경고 (advisory)

## 예시 (OK)

```
fix: probe_redfish.py 펌웨어 5.x 응답 형식 정정

- 원인: iDRAC9 5.x 펌웨어부터 SystemId path 변경
- adapter dell_idrac9.yml의 collect.systems_path 수정
- baseline_v1/dell_idrac9_baseline.json 회귀 추가
```

```
harness: rule 22 fragment-philosophy 보강

- R9 self-test (validate-fragment-philosophy skill) 추가
- 의심 패턴 9종 명시
```

```
feat: Huawei vendor adapter 추가
```

## 예시 (NG)

- `버그수정` — 금지어 단독
- `fix: 수정` — subject 전부 금지어
- `Huawei adapter 추가` — type prefix 누락
- `feat(adapter): ...` — scope 괄호 사용 안 함

## 강제 수준

- `commit_msg_check.py` (commit-msg hook): advisory (위반 시 stderr 경고, commit 허용)
- `pre_commit_*` hooks: 일부는 차단 (보호 경로 / 잔재 어휘 / SKILL.md 형식)

## 설치

```bash
bash scripts/ai/hooks/install-git-hooks.sh
```

## 관련

- script: `scripts/ai/hooks/commit_msg_check.py`
- self-test: `python scripts/ai/hooks/commit_msg_check.py --self-test`
