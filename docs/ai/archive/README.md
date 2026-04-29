# archive — server-exporter docs/ai 역사 reference

> rule 70 R6 archive 진입 기준 (cycle-013에서 진입):
> - **archive**: 구조·정책 전환의 결정 이력 / 완결된 cycle 로그 / Deprecated active 문서 과거본
> - **물리 삭제**: 1회성 빌드/배포 로그 / 1회성 cleanup 보고서 / PR description 복제본

## 진입 항목 (cycle-013, 2026-04-29)

### harness/ (cycle-001~005)

cycle-006부터는 active catalog (`docs/ai/harness/`)에 잔존. cycle-001~005는 초기 cycle (Plan 1~3 골격 + 첫 자기개선 dry-run + DRIFT 발견 / 정리)로 역사 reference.

- `cycle-001.md` — 자기개선 루프 dry-run
- `cycle-002.md` — 실측 + DRIFT 발견
- `cycle-003.md` — DRIFT 정리 + scan_suspicious_patterns 신규
- `cycle-004.md` — 도구 3종 정밀화 + 13 adapter origin
- `cycle-005.md` — DRIFT-007 catalog 정합 + scan 0건

### impact/ (6 보고서)

구조·정책 전환의 분석 reasoning 보존:

- `2026-04-27-suspicious-pattern-scan.md` — cycle-003 첫 scan
- `2026-04-27-vendor-boundary-57.md` — vendor 경계 57건 분석 → DRIFT-006 reasoning
- `2026-04-28-cisco-ta-unode-g1-analysis.md` — Cisco 검증 분석
- `2026-04-28-field-dictionary-coverage.md` — schema coverage 분석
- `2026-04-28-requirements-verification.md` — REQUIREMENTS 검증
- `2026-04-28-win10-winrm-setup.md` — Win10 WinRM 환경 분석

## 보존 정책

- archive 안 항목은 **변경 안 함** (역사 record).
- active catalog는 archive 항목을 reference 가능 (예: ADR이 archive 보고서를 인용).
- 추후 archive 진입 후보: cycle-006/007 (active 6+ cycle 잔존 시 — 현재 cycle-013 기준 active=cycle-006~012, archive 후보 없음).
