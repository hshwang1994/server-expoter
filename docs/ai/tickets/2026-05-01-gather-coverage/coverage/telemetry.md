# Coverage — telemetry 영역 (TelemetryService / MetricReport) — 신규 검토

## 채널

- **Redfish only** — TelemetryService root
- 우리 server-exporter **미수집** (Redfish 2018.2+ 신규 영역)

## 표준 spec (R1)

### 표준 path
- `/redfish/v1/TelemetryService` (root)
- `/TelemetryService/MetricDefinitions/{id}` — metric 정의 (CPU temp, power, etc.)
- `/TelemetryService/MetricReportDefinitions/{id}` — report 정의 (수집 주기 / 어떤 metric)
- `/TelemetryService/MetricReports/{id}` — 실 report 데이터
- `/TelemetryService/Triggers/{id}` — alert trigger

### MetricReport 필드
- `MetricValues[]`: MetricId / MetricValue / Timestamp / MetricProperty
- `ReportSequence` / `Timestamp`

## Vendor 호환성 (R2)

| Vendor | TelemetryService | MetricReport |
|---|---|---|
| Dell iDRAC 9 | OK (24+ report types) | iDRAC Telemetry Reference Tools |
| HPE iLO 5/6 | OK (periodic metric) | iLO Telemetry service |
| Lenovo XCC | 부분 | |
| Supermicro X12+ | 부분 | |
| Cisco CIMC | 부분 | |
| OpenBMC | 신규 도입 중 | |

## 우리 코드 영향

**현재 미수집**. server-exporter 는 instantaneous gather — telemetry 는 시계열 수집 영역 (별도 시스템).

## fix 후보

### F30 — Telemetry MetricReport 수집 (P3 — 사용자 요구 시)
- **변경 (Additive)**: 신규 섹션 'telemetry' 또는 별도 채널
- **scope**: 운영 모니터링 시스템 (Prometheus / Grafana 통합) 영역
- **우선**: P3 (현재 server-exporter scope 외)

## Sources

- [DMTF Redfish Telemetry White Paper](https://www.dmtf.org/sites/default/files/standards/documents/DSP2051_1.0.0.pdf)
- [HPE iLO Telemetry service](https://servermanagementportal.ext.hpe.com/docs/redfishservices/ilos/supplementdocuments/ilotelemetryservice)
- [Dell iDRAC Telemetry Reference Tools](https://github.com/dell/iDRAC-Telemetry-Reference-Tools)

## 갱신 history

- 2026-05-01: 신규 영역 ticket / F30 P3 (scope 외)
