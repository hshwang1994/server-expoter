# Technology Scope — server-exporter (2026-04-27)

> 기술 범위 / 향후 방향. 정기 갱신 (분기 / 큰 변경 시).

## 현재 (2026-04-27)

### 기술 스택 (정본: REQUIREMENTS.md 4절)

- ansible-core 2.20.3 + Python 3.12.3 + Java 21 (Jenkins Agent)
- Jinja2 3.1.6
- Collections: ansible.windows 3.3.0 / community.vmware 6.2.0 / community.windows 3.1.0 / ansible.posix 2.1.0 / community.general 12.4.0 / ansible.utils 6.0.1
- pip: pywinrm 0.5.0 / pyvmomi 9.0.0 / redis 7.3.0 / jmespath 1.1.0 / netaddr 1.3.0 / lxml 6.0.2

### 채널 / Vendor

- 3-channel: os / esxi / redfish
- 5 vendor: Dell / HPE / Lenovo / Supermicro / Cisco + generic fallback
- Adapter 25개 (redfish 14 + os 7 + esxi 4)
- Schema 10 sections + 28 Must

### 운영

- Jenkins multi-pipeline 3종 (main / grafana / portal)
- 4-Stage (Validate / Gather / Validate Schema / E2E Regression)
- Multi-loc (ich / chj / yi)
- agent-master 망 분리 (Ingest / Callback은 master)

### AI 하네스 (2026-04-27 신규)

- 29 rules + 43 skills + 51 agents + 10 policy + 6 role + 12 ai-context + 10 templates + 5 commands
- 19 hooks + 8 supporting scripts
- 7 외부 시스템 reference
- 약 25 docs/ai/ 운영 메타 문서

## 향후 방향 (Tentative)

### 단기 (1~3개월)

- 새 vendor 검토 (Huawei / NEC / Inspur / Ampere — PO 결정)
- 펌웨어 업그레이드 대응 (probe-redfish-vendor + baseline 갱신)
- harness-cycle 정기 실행 도입 (현재 수동만)
- incoming-review hook 실 환경 검증

### 중기 (3~6개월)

- IPMI fallback 지원 검토 (Redfish 미지원 BMC)
- 새 채널 검토 — 예: Kubernetes worker / 컨테이너 host
- Round 검증 자동화 (CI에 연결)
- catalog 자동 갱신 hook (rule 28 trigger)

### 장기 (6~12개월)

- 외부 시스템 응답 schema validation (JSON Schema 또는 Pydantic)
- 출력 schema versioning (v1 → v2 마이그레이션)
- Multi-loc 확장 (새 site 추가)
- Cost-aware 측정 (probe 빈도 / fact cache 효율)

## 기술 부채

- (현재 식별된 것 없음. CONVENTION_DRIFT.md / FAILURE_PATTERNS.md 누적되며 발견)

## 의존성 stale 위험

| 의존성 | 위험 | 대응 |
|---|---|---|
| ansible-core 2.20.3 | EOL 알림 시 | 분기 점검 |
| pyvmomi 9.0.0 | vSphere 새 버전 (8.x → 9.x) | 새 ESXi adapter |
| pywinrm 0.5.0 | Windows Server 2025 호환 | 검증 |
| Python 3.12 | 3.13/3.14 도입 시 | 단계적 |

## 정본 reference

- `REQUIREMENTS.md` (정본)
- `docs/01_jenkins-setup` ~ `docs/19_decision-log`
- `docs/ai/decisions/` ADR
