# Session Handoff — 다음 세션 시작점

> 본 문서는 다음 세션 (또는 다른 작업자) 이 cold-start 로 작업 이어가기 위한 마스터 가이드.
> 모든 ticket을 처리할 수 있도록 단계별 가이드 제공.

## 1. 첫 답변 시 작업자가 읽을 순서

1. **본 문서 (SESSION-HANDOFF.md)** — 시작점
2. [INDEX.md](./INDEX.md) — 전체 ticket 목차
3. [COMPATIBILITY-MATRIX.md](./COMPATIBILITY-MATRIX.md) — 적용된 41건 호환성 + 후보
4. [LAB-INVENTORY.md](./LAB-INVENTORY.md) — lab 보유 vs 부재 장비
5. [HARNESS-RETROSPECTIVE.md](./HARNESS-RETROSPECTIVE.md) — 2주간 사고/부족 회고
6. 작업할 ticket의 `fixes/F##.md`

## 2. 핵심 사용자 의도 (절대 잊지 마라)

| 원칙 | 의미 |
|---|---|
| **호환성 fallback only** | 새 데이터(json) 추가 / 새 섹션 / 새 vendor 추가는 **scope 외** |
| **Additive only** | 기존 path/동작 유지 + 신 환경 호환만 추가 |
| **lab 한계 → web 검색이 fixture 대체** | 우리 lab 부재 영역은 web 문서 / GitHub issue / vendor docs 기반 |
| **기술 안 되면 skip** | 예: ESXi InfiniBand는 vendor 의도상 Ethernet 인식 → skip 명시 |
| **보안 완화** (cycle 2026-05-01) | 하네스에 모든 권한. 보호 경로 / pre-commit advisory 다수 |

## 3. 현재 적용 상태 (cycle 2026-04-30 + 2026-05-01)

### 적용된 호환성 fallback (41건 / 15 카테고리 A~M)

자세히: [COMPATIBILITY-MATRIX.md](./COMPATIBILITY-MATRIX.md)

핵심 cycle commit:
```
fdf9dd5a revert: diagnosis.details.detail 키 제거 (호환성 외)
9eb11fe4 feat: redfish 404 분류 + PowerSubsystem fallback (DMTF 2020.4)
a483811b feat: 3채널 not_supported 인프라
3a0f2597 hotfix: Accept 헤더만 (Lenovo XCC reverse regression 정정)
7b0afc0c fix: 401/403 강제 failed (vault fallback 정상화)
4715bb5b fix: HTTP 헤더 호환 + 405/406 허용
```

### 36 fix 후보 분류

- **호환성 fallback (사용자 의도) 22건** — P1: 3 / P2: 8 / P3: 11
- **호환성 외 (별도 cycle) 12건** — 새 데이터 / 새 섹션 / 새 vendor

## 4. 다음 세션 시작 — P1 작업 (즉시)

### F05 — power EnvironmentMetrics fallback (P1)
- 위치: `redfish_gather.py` `_gather_power_subsystem`
- 변경 (Additive): EnvironmentMetrics 200 OK 시 PowerControl 정보 추출
- 회귀: lab Gen12 / XCC2-3 BMC fixture
- ticket: [fixes/F05.md](./fixes/F05.md)

### F13 — Cisco CIMC AccountService 'not_supported' 분류 (P1)
- 위치: `redfish_gather.py` `account_service_get`
- 변경 (Additive): 404/read-only 응답 시 unsupported list 분류 (cycle 2026-05-01 인프라)
- ticket: [fixes/F13.md](./fixes/F13.md)

### F23 — OS gather 'not_supported' 점진 전환 (P1)
- 위치: `os-gather/tasks/{linux,windows}/gather_*.yml`
- 변경 (Additive): 명령 부재 (lspci 등) 시 `_sections_unsupported_fragment` set
- 묶음: F07 (Linux IB lspci 부재)
- ticket: [fixes/F23.md](./fixes/F23.md)

## 5. P2 작업 (lab 검증 / 사고 재현 후) — 8건

| 우선 | ID | 영역 | 핵심 변경 | 검증 |
|---|---|---|---|---|
| P2-1 | F02 | cpu | ProcessorType 'Accelerator'/'Core' 통과 | normalize_standard.yml:25-32 |
| P2-2 | F04 | network_adapters | HPE iLO 5 BaseNetworkAdapters fallback | 구 펌웨어 lab 또는 web fixture |
| P2-3 | F08+F13 | users | Cisco AccountService (F13 묶음) | F13과 함께 |
| P2-4 | F10 | memory | HPE Gen11 HBM enum (자동 통과 검증) | Gen11 fixture |
| P2-5 | F12 | power | Cisco CIMC PowerSubsystem 검증 | Cisco lab 검증 |
| P2-6 | F17 | 횡단 | Schema errata 사용 | DMTF release notes 추적 |
| P2-7 | F20 | users | backoff 1초 → 5초 | try_one_account.yml:70 |
| P2-8 | F21 | OS Linux | paramiko ssh-rsa legacy 호환 | RHEL 9 + 구 Linux 사고 재현 |

## 6. P3 작업 (검증만 또는 사고 재현 시) — 11건

F01 / F09 / F11 / F14 / F15 / F22 / F24 / F33~F36 / F40

## 7. R6 InfiniBand (4건) — 호환성

| ID | 채널 | 우선 |
|---|---|---|
| F37 | Linux IB 도구 부재 graceful (F07 묶음) | P3 |
| F38 | Windows IB NIC 분류 (Mellanox VEN_15B3) | P3 |
| F39 | ESXi IB skip (vendor 의도) | P4 |
| F40 | Redfish ConnectX VPI mode (이미 호환) | P3 검증만 |

## 8. R7 추가 호환성 (2026-05-01 web 검색 R7)

### F41 — community.vmware 6.2.0 → 7.0.0 호환성 추적
- 일부 모듈 deprecated (vmware_maintenancemode, vmware_vm_inventory)
- 우리 esxi-gather 영향 추적 — 사용 모듈 검토
- 우선: **P2** (다음 ansible upgrade cycle)

### F42 — Redfish v2 path 향후 호환성 (추적만)
- 현재 `/redfish/v1/` 하드코딩 (`_p()`)
- 메이저 버전 변경 시 backward incompatible
- 2026 현재 v1 만 사용 — DMTF 미발표
- 우선: **P3** (추적만)

### F43 — RHEL 10 crypto policy SHA-1 호환
- RHEL 10 DEFAULT 가 RHEL 9 보다 완화 (TLS 외 SHA-1 허용)
- 우리 SECLEVEL=0 + LEGACY 옵션 호환 가정
- 우선: **P3** (RHEL 10 도입 시 검증)

## 9. 호환성 외 (별도 cycle — 사용자 명시 승인 필요)

12건 — F03/F06/F19/F26/F27/F28/F29/F30/F31/F32/F18/F25.
이 영역은 **사용자 명시 승인 받은 후만 진행** (rule 92 R5 schema 변경 / rule 50 R4 vendor 추가 등).

## 10. 다음 세션 작업자 가이드라인

### 시작 시 명시할 것
1. "본 cycle 호환성 영역만 작업"
2. "P1 (F05 / F13 / F23) 부터 시작"
3. "각 fix 별 ticket 의 'Cold-start' 절 따름"

### 진행 시 명시할 것
- **Additive only** — 기존 path / 동작 유지 검증
- **lab 한계 시 web 검색** — sources 명시 (rule 96 R1 origin 주석)
- **회귀 테스트 의무** — pytest + verify_harness_consistency
- **3채널 fragment 인프라** 활용 (`_sections_unsupported_fragment`)

### 완료 시 (rule 24 R9)
6 체크리스트:
1. 정적 검증 (pytest / py_compile / yaml syntax)
2. 발견 가능한 버그 0건
3. 문서 4종 갱신
4. 후속 식별 (NEXT_ACTIONS)
5. 태그 (해당 시)
6. 회귀 (영향 vendor)

## 11. 자주 사용할 도구

- **Web 검색**: `WebSearch` tool (server-exporter 환경에서 사용 가능)
- **회귀**: `python -m pytest tests/unit/`
- **harness 일관성**: `python scripts/ai/verify_harness_consistency.py`
- **vendor 경계**: `python scripts/ai/verify_vendor_boundary.py`
- **PROJECT_MAP drift**: `python scripts/ai/check_project_map_drift.py`

## 12. 참조 문서 (정본)

- `CLAUDE.md` — 프로젝트 전체 개요 + 자율 판단 원칙
- `GUIDE_FOR_AI.md` — Fragment 철학 / 새 gather 템플릿
- `REQUIREMENTS.md` — 벤더/버전별 최소 요구사항
- `.claude/rules/` — 28 rule (rule 13 R5 envelope / rule 22 fragment / rule 92 R5 schema 변경 / rule 96 외부 계약)
- `docs/01~19` — 운영 문서

## 13. 갱신 history

- 2026-05-01: 초안 작성. 다음 세션 cold-start 가이드.
