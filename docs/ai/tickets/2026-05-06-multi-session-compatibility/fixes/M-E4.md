# M-E4 — vendor-boundary-map.yaml 갱신

> status: [PENDING] | depends: M-E2 | priority: P2 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

M-E2 adapter 추가 → policy/vendor-boundary-map.yaml 동기화 (rule 12 / rule 50 R2 단계 7).

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `.claude/policy/vendor-boundary-map.yaml` |
| 리스크 | LOW |

## 작업 spec

```yaml
# .claude/policy/vendor-boundary-map.yaml (기존 entry 보강)

vendors:
  hpe:
    aliases: ["HPE", "Hewlett Packard Enterprise", "Hewlett-Packard", "HP"]
    bmc_names: ["iLO 5", "iLO 6", "iLO 7"]
    bmc_names_special:  # 신규 — Superdome 추가 (M-E2)
      - context: "Superdome Flex / Flex 280"
        bmc: "iLO 5 + RMC"
    adapters:
      # 기존 hpe_proliant_gen10 / 11 / 12 외에 추가
      - hpe_superdome.yml (cycle 2026-05-06)
      - hpe_superdome_flex_280.yml (cycle 2026-05-06)
      - hpe_superdome_legacy.yml (cycle 2026-05-06)
```

→ M-E1 결정 (b) 별도 vendor 시:

```yaml
vendors:
  superdome:  # 신규 vendor entry
    aliases: ["HPE Superdome", "HPE Integrity"]
    bmc_names: ["iLO 5 + RMC", "OA"]
    adapters:
      - superdome_flex_280.yml
      - superdome_flex.yml
      - superdome_legacy.yml
```

## 회귀 / 검증

- yamllint policy/vendor-boundary-map.yaml
- `python scripts/ai/verify_vendor_boundary.py` (rule 12)

## risk

- (LOW) yaml 형식 오류만 주의

## 완료 조건

- [ ] vendor-boundary-map.yaml 갱신 (M-E1/E2 결정 따라)
- [ ] verify_vendor_boundary PASS
- [ ] commit: `docs: [M-E4 DONE] vendor-boundary-map Superdome entry`

## 다음 세션 첫 지시 템플릿

```
M-E4 vendor-boundary-map 갱신.

선행: M-E2 [DONE]
작업: .claude/policy/vendor-boundary-map.yaml 갱신
```

## 관련

- rule 12 R1
- rule 50 R2 단계 7
- policy: .claude/policy/vendor-boundary-map.yaml
