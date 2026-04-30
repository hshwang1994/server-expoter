# Gather Coverage Tickets — 2026-05-01

> server-exporter 의 모든 gather 섹션에 대해 외부 시스템 (Redfish API + OS Linux/Windows + ESXi vSphere)
> 호환성 / 표준 변천 / 알려진 사고 패턴을 전수 조사한 티켓 모음.
> 세션 종료 후 다른 작업자(또는 같은 세션의 cold start)가 cycle 이어 진행할 수 있도록 자세히 기록.

## 진행 상태

| 단계 | 상태 | 비고 |
|---|---|---|
| Phase A — 기존 cycle 티켓화 | [DONE] | CYCLE-04-30 / CYCLE-05-01 / COVERAGE-MAIN 작성 완료 |
| Phase B Round 1 — DMTF 표준 13 영역 | [DONE] | coverage/MATRIX-R1.md (12 영역 검색 + 8건 fix 후보 발견) |
| Phase B Round 2 — Vendor 펌웨어 호환성 | [DONE] | coverage/MATRIX-R2.md (5 vendor × BMC 세대 매트릭스 + 7건 신규 fix 후보 F9~F15) |
| Phase B Round 3 — 알려진 사고/함정 | [TODO] | 13 영역 |
| Phase C — OS/ESXi 채널 3 round | [TODO] | SSH/WinRM/vSphere/esxcli |
| Phase D — 종합 매트릭스 + push | [TODO] | |

## 티켓 파일

### Cycle 작업 (이미 적용된 commit)

- [CYCLE-2026-04-30.md](./CYCLE-2026-04-30.md) — HTTP 406 호환 fix + Lenovo XCC reverse regression hotfix + 401/403 vault fallback 정상화 + verbosity 토글
- [CYCLE-2026-05-01.md](./CYCLE-2026-05-01.md) — 404→'not_supported' 분류 + PowerSubsystem fallback (DMTF 2020.4) + 3채널 fragment 인프라

### Coverage 조사 (gather 영역별)

- [COVERAGE-MAIN.md](./COVERAGE-MAIN.md) — 메인 진행 상태 + 종합 매트릭스
- coverage/ 디렉토리:
  - [system.md](./coverage/system.md)
  - [bmc.md](./coverage/bmc.md)
  - [cpu.md](./coverage/cpu.md)
  - [memory.md](./coverage/memory.md)
  - [storage.md](./coverage/storage.md)
  - [network.md](./coverage/network.md)
  - [network_adapters.md](./coverage/network_adapters.md)
  - [firmware.md](./coverage/firmware.md)
  - [users.md](./coverage/users.md)
  - [power.md](./coverage/power.md)
  - [thermal.md](./coverage/thermal.md)
  - [hba_ib.md](./coverage/hba_ib.md)
  - [runtime.md](./coverage/runtime.md)

## 작업자 가이드 (세션 cold start)

1. **현재 적용된 cycle**: CYCLE-04-30 + CYCLE-05-01 둘 다 main에 적용 + push 완료. 5 vendor BMC 호환성 + 인프라 마련됨.
2. **진행 중**: COVERAGE 조사. 각 coverage/{section}.md 의 "진행 상태" 표 확인.
3. **다음 작업**:
   - 진행 상태가 [TODO] 인 영역 → 다음 round 진행
   - [WIP] → 진행 중인 round 마무리
   - [DONE] → 다음 단계 진행
4. **검색 방법**: WebSearch 도구 (server-exporter 내 사용 가능).
5. **티켓 갱신**: 각 round 후 coverage/{section}.md 의 "Round N" 절에 결과 + sources 추가.

## 마무리 조건 (사용자 명시 2026-05-01)

> "검색 - 티켓저장 - 검색 - 티켓저장 계속 반복. 우리 개더링에서 더이상 검색할게없으면 그때 종료. 있다면 계속 반복. 검색과 검증을 한번만하고 끝내지말고 최소 3번은 해라"

→ 모든 영역 최소 3 round 완료 + 추가 검색 항목 0건 도달 시 cycle 종료.

## 관련 rule

- rule 96 (external-contract-integrity) — origin 주석 + drift 추적
- rule 95 R1 #11 (외부 계약 drift 의심)
- rule 70 R1 (문서 갱신 매핑)
- rule 13 R5 (envelope 13 필드 — sections enum 영향)

## 갱신 history

- 2026-05-01: INDEX 생성, Phase A 진입
