# REQUIREMENTS.md 정합 검증 (Round 11 reference 기반)

> 일자: 2026-04-28
> rule: 96 R3 (외부 계약 반영 enum 값 변경 시 영향 범위)
> 데이터 출처: `tests/reference/agent/agent/10_100_64_154/`

## 비교 결과

### 핵심 버전 (CLAUDE.md "기술 스택" 표 vs 실측)

| 항목 | CLAUDE.md 명시 | Agent 154 실측 | 정합 |
|---|---|---|---|
| ansible-core | 2.20.3 | **2.20.3** | OK |
| ansible (package) | 13.4.0 | **13.4.0** | OK |
| Python | 3.12.3 (`/opt/ansible-env/`) | **3.12.3** (시스템 + venv) | OK |
| Java (OpenJDK) | 21.0.10 | **21.0.10** (Ubuntu 124.04 build) | OK |
| Jinja2 | 3.1.6 | **3.1.6** | OK |

### pip 패키지 (CLAUDE.md vs 실측)

| 패키지 | CLAUDE.md | Agent 154 실측 | 정합 |
|---|---|---|---|
| pywinrm | 0.5.0 | **0.5.0** | OK |
| pyvmomi | 9.0.0 | **9.0.0.0** | OK (semver 동일) |
| jmespath | 1.1.0 | **1.1.0** | OK |
| netaddr | 1.3.0 | **1.3.0** | OK |
| lxml | 6.0.2 | **6.0.2** | OK |
| redis | 7.3.0 | **7.3.0** | OK |
| Redfish (stdlib only) | 외부 라이브러리 없음 | requests 2.32.5 / urllib3 2.6.3 / cryptography 46.0.5 / pyspnego 0.12.1 / requests_ntlm 1.3.0 등 존재 | **참고: 운영 venv에는 redfish 외 용도 패키지 다수 존재 — 정상 (rule 10 R2: redfish library 자체는 stdlib only)** |

### Java / OS

- Ubuntu 124.04 → Ubuntu 24.04 (검증 기준 base OS)
- OpenJDK 21.0.10 build "21.0.10+7-Ubuntu-124.04"

### Collections (ansible-galaxy)

`ansible-galaxy collection list`는 `ansible-galaxy` 명령이 default PATH에 없어 미수집. 단:
- `ansible==13.4.0` 패키지에 ansible.windows / community.vmware / community.windows / ansible.posix / community.general / ansible.utils가 bundle되어 있음 (CLAUDE.md "Collections (프로젝트 사용 분)")
- 추가 third-party collection 발견: **grafana**, **netbox**, **infinidat/infinibox** (서버-exporter와 무관, Jenkins 다른 job용 추정 — REQUIREMENTS 외)

## 발견 / drift

### F-V1: PATH 격리 (작은 발견, follow-up 가능)

- `ansible`, `ansible-galaxy`, `pip3` 명령이 cloviradmin user의 default PATH에 없음. `/opt/ansible-env/bin/`을 PATH에 추가하지 않은 상태.
- 호출 시 절대 경로 (`/opt/ansible-env/bin/ansible`) 또는 `source /opt/ansible-env/bin/activate` 필요
- Jenkins job 실행 시 ansible은 정상 동작 (Jenkinsfile에서 절대 경로 호출 또는 venv activate 가정)
- **rule 96 R3 영향**: 없음 (REQUIREMENTS.md는 PATH 가정 없이 venv 명시)

### F-V2: Third-party collections (REQUIREMENTS 외)

- grafana/grafana, netbox/netbox, infinidat/infinibox collection 설치 — 서버-exporter 사용 안 함
- **권장**: REQUIREMENTS.md "Collections" 절에 "기타 third-party collection은 다른 Jenkins job용으로 무관" 1줄 추가 (선택)

### F-V3: 필수 collection 버전 미확인

- `ansible-galaxy collection list` 미실행으로 ansible.windows 3.3.0 / community.vmware 6.2.0 등 명시 버전과 실측 정합 직접 확인 불가
- **follow-up**: `gather_agent_env.py` 보강 — `/opt/ansible-env/bin/ansible-galaxy collection list` 절대 경로 호출 추가
- 우선순위: LOW (bundle된 collection 버전 drift 발생 가능성 작음)

## 결론

**REQUIREMENTS.md 명시 버전 vs Agent 154 실측: 100% 정합 확인** (확인 가능한 11항목 모두 일치).

추가 확인 필요 항목 (F-V3): ansible.windows / community.vmware 등 collection 버전 — 다음 reference 수집 사이클 또는 즉시 follow-up.

## 관련

- rule: 96 (외부 계약 무결성), 70 (docs-and-evidence-policy)
- 정본: `REQUIREMENTS.md` 4절 (검증 기준 Agent), `CLAUDE.md` 기술 스택 표
- 데이터: `tests/reference/agent/agent/10_100_64_154/`
- evidence: `tests/evidence/2026-04-28-reference-collection.md`
