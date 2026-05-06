# M-E5 — README / docs 갱신 (Superdome)

> status: [PENDING] | depends: M-E2 | priority: P2 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

Superdome 추가를 README / docs 에 반영 (rule 50 R2 단계 8).

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `README.md`, `docs/13_redfish-live-validation.md`, `docs/19_decision-log.md`, `CLAUDE.md` (벤더 표) |
| 리스크 | LOW |

## 작업 spec

### (1) README.md

벤더 list 에 추가 (또는 HPE sub-line 명시):

```markdown
**특징:**
- **3중 채널**: OS-gather + ESXi-gather + Redfish-gather
- **Fragment 모듈화**
- **Adapter 시스템**: 벤더/세대별 수집 방식 YAML 추상화
- **멀티벤더**: Dell / HPE (ProLiant + **Superdome Flex / Flex 280**) / Lenovo / Supermicro / Cisco
```

### (2) docs/13_redfish-live-validation.md

Round 검증 list 에 entry 추가:

```markdown
## Round NN — HPE Superdome (lab 부재, web sources only) — 2026-05-06

- 적용 adapter: hpe_superdome_flex_280.yml / hpe_superdome.yml / hpe_superdome_legacy.yml
- 검증 방식: 정적 분석 + mock fixture (M-D4)
- lab: 0 — 사이트 도입 시 capture-site-fixture skill 적용
- sources: M-E1 web 검색 (HPE 공식 docs / DMTF)
```

### (3) docs/19_decision-log.md

```markdown
## 2026-05-06 — HPE Superdome vendor 추가 (cycle multi-session-compatibility)

### 결정
- (a) HPE sub-line 으로 분류 또는 (b) 별도 vendor — M-E1 결정 결과
- adapter 3 종 (Flex / Flex 280 / Legacy) priority=70~90
- lab 부재 → web sources only (rule 96 R1-A)

### 근거
- 사용자 명시 (2026-05-06): "superdome 하드웨어도 벤더 추가해줘"
- HPE Superdome Flex / Flex 280 의 iLO 5 + RMC 구조 식별
- Legacy Superdome 2 / X / Integrity 는 graceful_degradation 분류

### 영향
- adapter 38 → 41 (+3)
- vendor 정규화 9 → 9 (HPE sub-line) 또는 10 (별도 vendor)
```

### (4) CLAUDE.md (선택)

벤더 표 갱신 (멀티벤더 list 에 Superdome 명시).

## 회귀 / 검증

- 마크다운 정합성
- 링크 무결성

## risk

- (LOW) docs 만

## 완료 조건

- [ ] README.md 갱신
- [ ] docs/13_redfish-live-validation.md Round entry 추가
- [ ] docs/19_decision-log.md entry 추가
- [ ] (선택) CLAUDE.md 갱신
- [ ] commit: `docs: [M-E5 DONE] Superdome README / live-validation / decision-log`

## 다음 세션 첫 지시 템플릿

```
M-E5 docs 갱신 진입.

선행: M-E2 [DONE]
작업:
1. README.md 멀티벤더 list 갱신
2. docs/13_redfish-live-validation.md Round entry
3. docs/19_decision-log.md entry
```

## 관련

- rule 50 R2 단계 8
- rule 70 R1 (변경 종류 → 갱신 매핑)
