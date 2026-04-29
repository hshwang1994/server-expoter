# 2026-04-30 Jenkins Full Lab Sweep — REPORT

> **시점**: main 머지(fc7f806c) 직후 / Jenkins master(10.100.64.152)에서 hshwang-gather job 직접 트리거 / 19 hosts 대상

## 트리거 환경

- **Jenkins master**: 10.100.64.152 (cloviradmin)
- **Jenkins URL**: http://localhost:8080 (master 내부)
- **Job**: `hshwang-gather`
- **Branch (Jenkins agent checkout)**: `main` @ fc7f806c
- **빌드 번호**: #117 (os) / #118 (esxi) / #119 (redfish)

## 결과 요약

| 채널 | 빌드 # | Jenkins result | duration | 호스트 | success | partial | failed |
|---|---|---|---|---|---|---|---|
| os | 117 | **SUCCESS** | 112.5s | 7 | **7** | 0 | 0 |
| esxi | 118 | **SUCCESS** | 39.5s | 3 | **3** | 0 | 0 |
| redfish | 119 | **SUCCESS** | 471.3s | 9 | **8** | 0 | 1* |

**총 19 hosts: 18/19 (94.7%) status=success**

*10.50.11.162는 BMC 자격증명 mismatch (NEXT_ACTIONS OPS-DELL-VAULT-1, 알려진 lab 운영 이슈).

## 호스트별 상세

### OS 채널 (#117 SUCCESS, 7/7)

| 호스트 | 벤더 | 분류 | sections success/not_supported | 핵심 검증 |
|---|---|---|---|---|
| 10.100.64.96 | dell | RHEL/Ubuntu (베어메탈) | 6/4 | Dell baremetal vendor 정확 |
| 10.100.64.135 | vmware | **Windows Server 2022** | **7/3** | 신규 — `vendor='vmware'` (B80 Windows fix 검증) / hardware section 활성 |
| 10.100.64.161 | vmware | **RHEL 8.10 (Python 3.6 raw fallback)** | 6/4 | B80 raw fix / IPv6 / lspci 모두 정상 |
| 10.100.64.163 | vmware | RHEL 9.2 | 6/4 | python_ok |
| 10.100.64.165 | vmware | RHEL 9.6 | 6/4 | python_ok |
| 10.100.64.167 | vmware | Ubuntu 24.04 | 6/4 | python_ok |
| 10.100.64.169 | vmware | Rocky 9.6 | 6/4 | python_ok |

### ESXi 채널 (#118 SUCCESS, 3/3)

| 호스트 | 벤더 | success/not_supported | 핵심 검증 |
|---|---|---|---|
| 10.100.64.1 | cisco | 6/4 | runtime.timezone="UTC" / firewall_state="enabled" / default_gateway 추출 |
| 10.100.64.2 | cisco | 6/4 | (동일) |
| 10.100.64.3 | cisco | 6/4 | (동일) |

### Redfish 채널 (#119 SUCCESS, 8/9 success + 1 failed)

| 호스트 | 벤더 | sections success/not_supported | 핵심 검증 |
|---|---|---|---|
| 10.100.15.27 | dell | 8/2 | mem.mfg='SK hynix' (canonical) |
| 10.100.15.28 | dell | 8/2 | (동일) |
| 10.100.15.31 | dell | 8/2 | (동일) |
| 10.100.15.33 | dell | 8/2 | (동일) |
| 10.100.15.34 | dell | 8/2 | (동일) |
| 10.50.11.231 | hpe | 8/2 | psu1 health=Critical (real lab) |
| 10.50.11.232 | lenovo | 8/2 | psu1 health=Critical (real lab) |
| 10.100.15.2 | cisco | 8/2 | mem.pn 길이 16 (trailing space strip 검증) |
| **10.50.11.162** | dell | **0/1 (status=failed)** | **BMC 자격증명 mismatch — vault dell.yml password 불일치** |

## 실패 호스트 분석 (10.50.11.162)

```json
{
  "ip": "10.50.11.162",
  "vendor": "dell",
  "status": "failed",
  "diagnosis": {
    "reachable": true,
    "port_open": true,
    "protocol_supported": true,
    "auth_success": null,
    "details": {
      "redfish_version": "1.17.0",
      "product": "Integrated Dell Remote Access Controller"
    }
  },
  "errors": [
    {
      "section": "redfish_gather",
      "message": "Redfish 수집 완전 실패 — BMC 연결 또는 인증 문제. ...",
      "detail": null
    }
  ]
}
```

- BMC 도달 OK (port 443) / Redfish API OK (1.17.0) / **인증 실패** (auth_success=null)
- `vault/redfish/dell.yml` 자격증명이 이 호스트 BMC에 안 맞음 (다른 4 Dell host는 성공)
- envelope 13 필드 모두 정상 emit (status=failed, errors[] 채움) — 호출자 시스템 호환성 OK
- 액션: **OPS-DELL-VAULT-1 (NEXT_ACTIONS)** — vault 회전 필요. 운영 결정 사항.

## envelope 13 필드 정합성

19 hosts 모두 13 필드 envelope emit (`schema_version, target_type, collection_method, ip, hostname, vendor, status, sections, diagnosis, meta, correlation, errors, data`). 실패 host도 동일 형식 (rule 13 R5 / rule 20 R1 정합).

## Jenkins 4-Stage 통과 검증

각 빌드 console log 확인:
- Stage 1 (Validate): inventory_json 파싱 OK
- Stage 2 (Gather): ansible-playbook 실행 (callback=json_only)
- Stage 3 (Validate Schema): field_dictionary 정합 통과 (FAIL 게이트)
- Stage 4 (E2E Regression): pytest baseline 통과

3 채널 모두 Stage 1-4 통과 → Jenkins result=SUCCESS.

## 검증 항목 매트릭스

| 항목 | 상태 |
|---|---|
| envelope.vendor 정상 (Linux baremetal/VMware) | PASS |
| envelope.vendor 정상 (Windows VMware — B80 신규) | **PASS** |
| envelope.vendor 정상 (ESXi cisco) | PASS |
| envelope.vendor 정상 (Redfish 5 vendor) | PASS |
| RHEL 8.10 raw fallback (Python 3.6) | PASS |
| 메모리 manufacturer canonical (Dell SK hynix) | PASS |
| Cisco PartNumber trailing space strip | PASS |
| ESXi runtime (timezone/firewall/ntp) | PASS |
| ESXi default_gateway extract | PASS |
| Linux IPv6 raw fallback | PASS |
| Linux NIC adapters (lspci) raw + python | PASS |
| Linux adapters schema 일관성 (raw=python) | PASS |
| Windows hardware section + bios_date ISO | PASS |
| 실패 host도 13 필드 envelope emit | PASS |

## 후속 작업

| 항목 | 분류 | 차단 사유 |
|---|---|---|
| OPS-DELL-VAULT-1 (10.50.11.162) | 운영 | vault dell.yml 자격증명 회전 필요 (BMC 측 변경) |
| 기타 lab 외부 의존 항목 | 외부 의존 | NEXT_ACTIONS 참조 |

## 원본

- 빌드 metadata: `_build_{os,esxi,redfish}.json`
- console log: `_console_{os,esxi,redfish}.txt` (300KB tail)
- envelope JSONL: `_envelope_{os,esxi,redfish}.jsonl` (host당 1줄)
- 실행 스크립트: `_runner_trigger.py`
- 요약: `_summary.json`
