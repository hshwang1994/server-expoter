# JENKINS_PIPELINES — server-exporter

> Jenkins multi-pipeline 3종 카탈로그. rule 28 #4-5 측정 대상 (TTL 7-14일).

## 일자: 2026-04-27 (Plan 3 초기 골격)

## 3종 Pipeline

| Jenkinsfile | 호출자 | 주 용도 |
|---|---|---|
| Jenkinsfile | 일반 호출자 | 3-channel 통합 수집 (메인) |
| Jenkinsfile_grafana | Grafana | Grafana 대시보드용 데이터 수집 (Ingest는 master) |
| Jenkinsfile_portal | Portal | Portal 호출 (Callback은 master) |

## 4-Stage (모든 Jenkinsfile 공통)

| Stage | 책임 | FAIL 게이트 |
|---|---|---|
| 1. Validate | 입력값 검증 (target_type / loc / inventory_json 형식) | YES |
| 2. Gather | ansible-playbook 실행 (해당 채널) | YES |
| 3. Validate Schema | field_dictionary 정합 (output_schema_drift_check) | YES |
| 4. E2E Regression | pytest baseline (영향 vendor) | YES |
| Post (callback) | json_only callback → JSON 출력 | NO (advisory) |

## agent-master 망 분리

| 단계 | 실행 위치 |
|---|---|
| Validate (Stage 1) | master |
| Gather (Stage 2) | agent (해당 loc) |
| Validate Schema (Stage 3) | agent 또는 master |
| E2E Regression (Stage 4) | master (baseline 비교) |
| Post / callback | master (Jenkinsfile_portal에서 명시) |
| Ingest (Grafana 데이터) | master (Jenkinsfile_grafana에서 명시, 8bd80c1 commit) |

## cron 인벤토리 (rule 28 #5)

| Jenkinsfile | cron | 트리거 |
|---|---|---|
| Jenkinsfile | (호출자가 직접 트리거, no cron) | manual / Portal API |
| Jenkinsfile_grafana | (정기 polling) | 운영자 결정 (사용자 확인 필요) |
| Jenkinsfile_portal | (호출자 의존) | manual |

상세 cron 표현식은 Jenkinsfile* 안에 직접 명시.

## 갱신 trigger (rule 28 #4 / #5)

- TTL 7-14일
- Jenkinsfile* 수정
- cron 표현식 변경 (사용자 명시 승인 필수, rule 80 + 92 R5)

## 측정 명령

```bash
grep -E "cron\(|triggers\s*\{" Jenkinsfile*
grep -E "callback_url" Jenkinsfile*
```

## callback URL (rule 31)

- 정규화: `url.strip().rstrip('/')`
- Method: POST
- Body: callback_plugins/json_only.py JSON envelope
- 보안: URL에 user:pass 형식 금지 (path/token만)

## 정본 reference

- `Jenkinsfile`, `Jenkinsfile_grafana`, `Jenkinsfile_portal` (정본)
- `docs/01_jenkins-setup.md`, `docs/04_job-registration.md`, `docs/17_jenkins-pipeline.md`
- `.claude/ai-context/infra/convention.md`
