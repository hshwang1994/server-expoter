# M-E3 — ai-context vendors/superdome.md

> status: [PENDING] | depends: M-E1 | priority: P2 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

M-E1 검색 결과 + M-E2 adapter spec 을 ai-context 로 영구화. 다음 세션 / AI 가 Superdome 작업 시 컨텍스트 로드.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `.claude/ai-context/vendors/superdome.md` (신규) 또는 `.claude/ai-context/vendors/hpe.md` 갱신 (M-E1 결정 (a) 시) |
| 영향 vendor | HPE Superdome |
| 리스크 | LOW |

## 작업 spec

### (a) 결정 (a) — HPE sub-line 시

`.claude/ai-context/vendors/hpe.md` 갱신:

```markdown
## Superdome 시리즈 (cycle 2026-05-06 추가)

### 모델 / BMC
- Superdome Flex 280 (2020+) — iLO 5 + RMC
- Superdome Flex (2017+) — iLO 5 + RMC
- Superdome 2 / X / Integrity (legacy) — Onboard Administrator (OA)

### Redfish 지원
- Flex 280 / Flex: 표준 Redfish (iLO 5)
- Legacy: 부분 지원 / 없음

### adapter 매핑
- adapters/redfish/hpe_superdome_flex_280.yml (priority=90)
- adapters/redfish/hpe_superdome.yml (priority=85)
- adapters/redfish/hpe_superdome_legacy.yml (priority=70)

### 특이사항
- Multi-partition (nPAR) — 향후 partitioning section 진입 시 처리
- RMC 는 보조 manager — iLO 5 가 primary
- Manager 두 entry (iLO 5 + RMC) 존재 시 primary_ilo 사용
```

### (b) 결정 (b) — 별도 vendor 시

`.claude/ai-context/vendors/superdome.md` (신규):

```markdown
# Superdome (HPE 별도 vendor 분류)

## Manufacturer
- "HPE Superdome" / "HPE Integrity"

## 시리즈
(상기 hpe.md 와 동일)

## adapter
- adapters/redfish/superdome_flex_280.yml
- adapters/redfish/superdome_flex.yml
- adapters/redfish/superdome_legacy.yml
```

## 회귀 / 검증

- (문서만)
- 정적 검증: yamllint / 마크다운 정합성

## risk

- (LOW) M-E1 결정 (a)/(b) 와 일관성 유지 의무

## 완료 조건

- [ ] M-E1 결정 따라 (a) hpe.md 갱신 또는 (b) superdome.md 신규
- [ ] commit: `docs: [M-E3 DONE] ai-context vendors Superdome entry`

## 다음 세션 첫 지시 템플릿

```
M-E3 ai-context Superdome 진입.

선행: M-E1 [DONE] 결정 (a)/(b)
작업: M-E1 결정 따라 (a) hpe.md 갱신 또는 (b) superdome.md 신규
```

## 관련

- rule 50 R2 (vendor 추가 9단계 — 본 ticket 은 단계 6)
- ai-context 디렉터리: .claude/ai-context/vendors/
