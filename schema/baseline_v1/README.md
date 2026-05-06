# schema/baseline_v1 — 회귀 검증용 표준 응답 샘플

> **이 폴더는** 서버별로 server-exporter 가 정상 동작했을 때의 출력 JSON 을 그대로 보존한 "정답지" 입니다.
> 코드를 변경한 뒤 이 정답지와 현재 출력을 비교하면, 의도치 않은 회귀가 있었는지 즉시 알 수 있습니다.

## 핵심 약속

- 이 폴더의 JSON 은 **수정하지 않습니다**. 새 정답지가 필요하면 별도 폴더 (예: `baseline_v2/`) 를 만들어 사용합니다.
- 각 파일은 callback (`callback_plugins/json_only.py`) 의 출력을 그대로 저장한 형태입니다.
- 식별자(serial_number, system_uuid 같은 DMI 정보) 는 권장 운영 모드 (sudo become 사용) 기준으로 기록되어 있습니다.

## 파일 명명 규칙

```
{vendor 또는 os}_baseline.json
```

| 파일 | 채널 | 검증 시 사용된 장비 |
|------|------|--------------------|
| `dell_baseline.json` | Redfish | Dell PowerEdge R740 (iDRAC 9 / FW 4.00) |
| `hpe_baseline.json` | Redfish | HPE ProLiant DL380 Gen11 (iLO 6 / FW 1.73) |
| `lenovo_baseline.json` | Redfish | Lenovo ThinkSystem SR650 V2 (XCC / FW 5.70) |
| `cisco_baseline.json` | Redfish | Cisco TA-UNODE-G1 (CIMC) |
| `esxi_baseline.json` | ESXi | ESXi 7.0.3 |
| `ubuntu_baseline.json` | OS (Linux) | Ubuntu 24.04 |
| `windows_baseline.json` | OS (Windows) | Windows Server |
| `rhel810_raw_fallback_baseline.json` | OS (Linux) | RHEL 8.10 — Python raw fallback 경로 검증 |

## 기준 시점

- 최초 수집일: 2026-03-23
- 최초 git HEAD: ea8b8a1

## 변경이 필요할 때

1. 실장비에서 새로 응답을 수집한다 (`tests/redfish-probe/probe_redfish.py` 등).
2. 새 응답을 `baseline_v2/` 같은 별도 폴더로 저장한다.
3. 운영 변경 사유 / 검증 환경을 `tests/evidence/<날짜>-<주제>.md` 와 `docs/19_decision-log.md` 에 기록한다.
4. 회귀 비교 도구의 기준 폴더를 `baseline_v1` → `baseline_v2` 로 점진 전환한다.

본 폴더의 파일은 절대 in-place 로 덮어쓰지 않는다는 점이 핵심입니다 — 그래야만 회귀의 의미가 보존됩니다.

---

## 함께 보면 좋은 자료

| 자료 | 용도 |
|------|------|
| `tests/fixtures/` | 회귀 테스트의 입력 (raw 응답) |
| `tests/evidence/` | Round 단위 검증 결과 |
| [`../../docs/09_output-examples.md`](../../docs/09_output-examples.md) | 채널별 응답 실제 예시 |
| [`../../docs/13_redfish-live-validation.md`](../../docs/13_redfish-live-validation.md) | 실장비 검증 라운드 |
| [`../../docs/20_json-schema-fields.md`](../../docs/20_json-schema-fields.md) | envelope 13 필드 + 65 필드 의미 사전 |
