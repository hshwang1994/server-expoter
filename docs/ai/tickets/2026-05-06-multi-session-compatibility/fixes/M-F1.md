# M-F1 — docs/20_json-schema-fields.md 신설

> status: [PENDING] | depends: — | priority: P2 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

> "redfish, os, esxi에 대해서 json스키마 키값이 무엇을 의미하는지 모르겠어 이것을 나타내는 문서가 하나 필요해."

→ 3 채널 envelope 13 필드 + sections 10 + Must/Nice/Skip 65 entries 의 의미 / 출처 / 정규화 규칙 명시 문서.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `docs/20_json-schema-fields.md` (신설) |
| 영향 vendor | (문서만 — 9 vendor 공통) |
| 함께 바뀔 것 | `docs/00_index.md` 또는 README docs list 갱신 (docs/01~19 → docs/01~20) |
| 리스크 | LOW (문서만) |

## 작업 spec

### docs/20_json-schema-fields.md 구조

```markdown
# 20. JSON 출력 스키마 키 의미

> server-exporter 의 표준 JSON envelope (13 필드) + sections (10) + field_dictionary (39 Must + 20 Nice + 6 Skip = 65 entries) 의 모든 키가 어떤 의미인지 명시.

## 1. Envelope 13 필드

정본: `common/tasks/normalize/build_output.yml`. 작성 순서:

| # | 필드 | 타입 | 의미 | 예시 | 정규화 규칙 |
|---|---|---|---|---|---|
| 1 | `target_type` | str | 수집 채널 분류 | "os" / "esxi" / "redfish" | 호출자 입력 그대로 |
| 2 | `collection_method` | str | 사용된 수집 방법 | "ansible" / "redfish" / "vmware" | target_type 따라 자동 |
| 3 | `ip` | str | 수집 대상 IP | "10.x.x.1" | 호출자 입력 (service_ip / bmc_ip) |
| 4 | `hostname` | str | 호스트 이름 | "server01" | gather 결과 또는 IP fallback |
| 5 | `vendor` | str/null | 정규화된 vendor | "dell" / "hpe" / null | vendor_aliases.yml 기반 |
| 6 | `status` | enum | 전체 수집 상태 | "success" / "partial" / "failed" | build_status.yml 판정 (M-A1 분석 참조) |
| 7 | `sections` | dict | 섹션별 status | `{cpu: success, memory: success, ...}` | 섹션별 supported / collected / failed / not_supported |
| 8 | `diagnosis` | dict | 진단 정보 | `{precheck: {...}, gather_mode: ..., details: [...]}` | precheck 4단계 + 기타 |
| 9 | `meta` | dict | 메타 정보 | `{loc: "ich", duration_ms: 1234, ...}` | 운영 정보 |
| 10 | `correlation` | dict | 추적 정보 | `{host_ip: ..., request_id: ...}` | 호출자 추적 |
| 11 | `errors` | list | error 기록 | `[{...}, ...]` | _errors_fragment 누적 |
| 12 | `data` | dict | 섹션별 데이터 | `{cpu: {...}, memory: {...}, ...}` | _data_fragment 누적 |
| 13 | `schema_version` | str | 스키마 버전 | "1" | inject 후 |

→ rule 13 R5 / rule 96 R1-B 정본.

## 2. Sections 10 정의

정본: `schema/sections.yml`.

| section | 의미 | 채널 | adapter 분기 |
|---|---|---|---|
| `system` | 호스트 식별 / 위치 | OS / ESXi / Redfish | 모든 vendor |
| `hardware` | 물리 하드웨어 (chassis / model / SN) | OS / ESXi / Redfish | 모든 vendor |
| `bmc` | BMC 정보 (펌웨어 / IP / 권한) | Redfish only | 모든 vendor |
| `cpu` | CPU 정보 | OS / ESXi / Redfish | 모든 vendor |
| `memory` | 메모리 정보 | OS / ESXi / Redfish | 모든 vendor |
| `storage` | 디스크 / 볼륨 | OS / ESXi / Redfish | 모든 vendor |
| `network` | NIC / IP / VLAN | OS / ESXi / Redfish | 모든 vendor |
| `firmware` | 펌웨어 버전 list | Redfish only | 모든 vendor |
| `users` | 계정 list | Redfish only | 모든 vendor |
| `power` | 파워 / 전력 | Redfish only | DMTF 2020.4 PowerSubsystem fallback |

## 3. Field Dictionary 65 entries (39 Must + 20 Nice + 6 Skip)

정본: `schema/field_dictionary.yml`.

### Must (39 entries) — 모든 vendor 보장

각 섹션별 필수 필드. 호출자가 모든 응답에서 보장 받음.

(field_dictionary.yml 의 Must entry 전수 list — table 으로)

### Nice (20 entries) — vendor-specific

#### Redfish 채널 vendor-specific

#### OS 채널 vendor-specific

### Skip (6 entries) — 의도적 미수집

(예: vendor 별 OEM 영역 중 노출 부적절한 내부 정보)

## 4. 채널별 차이

### Redfish 채널 envelope 예시

```json
{
  "target_type": "redfish",
  "collection_method": "redfish",
  "ip": "10.x.x.1",
  "vendor": "dell",
  "status": "success",
  "sections": {
    "system": "success",
    "bmc": "success",
    "cpu": "success",
    "memory": "success",
    "storage": "success",
    "network": "success",
    "firmware": "success",
    "users": "success",
    "power": "success",
    "hardware": "success"
  },
  ...
}
```

### OS 채널 envelope 예시

```json
{
  "target_type": "os",
  "collection_method": "ansible",
  ...
  "sections": {
    "system": "success",
    "cpu": "success",
    ...
    "bmc": "not_supported",  // OS 채널은 BMC 직접 수집 안 함
    "firmware": "not_supported",
    "users": "not_supported",
    "power": "not_supported"
  },
  ...
}
```

### ESXi 채널 envelope 예시

(유사하지만 storage / network 정규화 차이)

## 5. status 판정 규칙

(M-A1 분석 결과 반영)

- `success`: 모든 supported 섹션 success
- `partial`: 일부 success + 일부 failed (혼재)
- `failed`: 모든 supported failed 또는 supported 0

(M-A2 사용자 결정 결과 — "errors 있는데 success" 케이스 처리 규칙 반영)

## 6. errors[] 형식

```json
{
  "errors": [
    {
      "section": "storage",
      "code": "REDFISH_ENDPOINT_404",
      "message": "Volumes endpoint not found at /redfish/v1/Systems/1/Storage/.../Volumes",
      "severity": "warning",  // M-A2 (b) 결정 시
      "vendor": "dell",
      "timestamp": "2026-05-06T10:00:00Z"
    }
  ]
}
```

## 7. diagnosis.details 형식

```json
{
  "diagnosis": {
    "precheck": {
      "ping": "ok",
      "port": "ok",
      "protocol": "ok",
      "auth": "ok"
    },
    "gather_mode": "python_ok",  // OS 채널 — Linux 2-tier
    "python_version": "3.11.9",  // OS 채널
    "details": [
      {"step": "vendor_detect", "result": "dell"},
      ...
    ]
  }
}
```

## 8. correlation 형식

```json
{
  "correlation": {
    "host_ip": "10.x.x.1",
    "request_id": "uuid-...",
    "loc": "ich",
    "callback_url": "https://..."
  }
}
```

## 9. meta 형식

```json
{
  "meta": {
    "loc": "ich",
    "duration_ms": 1234,
    "started_at": "2026-05-06T10:00:00Z",
    "ended_at": "2026-05-06T10:00:30Z",
    "adapter_id": "dell_idrac9",
    "adapter_score": 100,
    "schema_version": "1",
    "exporter_version": "..."
  }
}
```

## 10. 호환성 정책 (rule 96 R1-B)

envelope 13 필드 추가 / 삭제 / 리네임 **금지** (호출자 시스템 파싱 영향). 새 데이터 / 새 필드는 별도 cycle (schema 변경 사용자 명시 승인 — rule 92 R5).

## 관련

- rule 13 R5 (envelope 13 필드 정본)
- rule 96 R1-B (envelope shape 변경 자제)
- rule 92 R5 (schema 변경 사용자 명시)
- skill: verify-json-output
- 정본 코드: `common/tasks/normalize/build_output.yml`
- 정본 schema: `schema/sections.yml`, `schema/field_dictionary.yml`
- baseline: `schema/baseline_v1/<vendor>_baseline.json`
```

→ 본 문서 = 호출자 시스템 / 새 작업자 / AI 가 envelope 키 의미 파악하는 정본 reference.

## 회귀 / 검증

- 마크다운 정합성
- field_dictionary.yml 의 65 entries 와 본 문서의 list 일치 검증

## risk

- (LOW) 정본 (`common/tasks/normalize/build_output.yml`, `schema/*`) 와 drift 위험 — drift 시 본 문서 갱신 책임 명시

## 완료 조건

- [ ] docs/20_json-schema-fields.md 신설 (위 10 절 모두)
- [ ] field_dictionary.yml 65 entries 모두 본 문서에 list
- [ ] M-A1 status 판정 규칙 반영 (analytic 후속)
- [ ] M-A2 사용자 결정 결과 반영 (가능 시 — 또는 placeholder + M-A2 [DONE] 후 갱신)
- [ ] commit: `docs: [M-F1 DONE] docs/20_json-schema-fields.md 신설 — envelope 13 + sections 10 + 65 entries`

## 다음 세션 첫 지시 템플릿

```
M-F1 JSON schema 의미 문서 진입.

읽기 우선순위:
1. fixes/M-F1.md
2. common/tasks/normalize/build_output.yml (envelope 13 정본)
3. schema/sections.yml (10 sections)
4. schema/field_dictionary.yml (65 entries)
5. schema/baseline_v1/dell_baseline.json (예시 1)
6. M-A1 분석 결과 (status 판정 규칙)
7. M-A2 사용자 결정 (있으면 반영)

작업:
1. docs/20_json-schema-fields.md 신설
2. 10 절 모두 채움
3. 65 entries 전수 list

선행: 없음 (M-A1 결과 있으면 풍부하게 작성 가능)
후속: M-F2 (3채널 비교)
```

## 관련

- rule 13 R5 / rule 96 R1-B
- skill: verify-json-output
