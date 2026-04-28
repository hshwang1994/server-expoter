# JENKINS_PIPELINES — server-exporter

> Jenkins multi-pipeline 3종 카탈로그. rule 28 #4-5 측정 대상 (TTL 7-14일).
> 실측 (`grep stage Jenkinsfile*`) — 2026-04-27.

## 3종 Pipeline 4-Stage 매트릭스 (실측)

| Pipeline | Stage 1 | Stage 2 | Stage 3 | Stage 4 |
|---|---|---|---|---|
| `Jenkinsfile` | Validate | Gather | Validate Schema | **E2E Regression** |
| `Jenkinsfile_grafana` | Validate | Gather | Validate Schema | **Ingest** (Grafana 데이터 적재) |
| `Jenkinsfile_portal` | Validate | Gather | Validate Schema | **Callback** (호출자 통보) |

**[INFO]** Plan/design 문서에서 "4-Stage = Validate/Gather/Validate Schema/**E2E Regression**" 으로 일반화 표기했으나, 실측 결과 **Stage 4가 Jenkinsfile별로 다름**.

## Stage별 책임

| Stage | 공통 (모든 3종) | Stage 4 차이 |
|---|---|---|
| 1. Validate | 입력 형식 (target_type / loc / inventory_json) | — |
| 2. Gather | ansible-playbook 실행 (해당 채널) | — |
| 3. Validate Schema | field_dictionary 정합 | — |
| 4. (pipeline별) | — | Jenkinsfile: pytest baseline 회귀 |
| | — | Jenkinsfile_grafana: Grafana 데이터 적재 (Ingest) |
| | — | Jenkinsfile_portal: 호출자 callback (Callback) |

## agent-master 망 분리 (이전 commit 8bd80c1 / 8b2f128 참조)

| Stage | Jenkinsfile | Jenkinsfile_grafana | Jenkinsfile_portal |
|---|---|---|---|
| Validate | master | master | master |
| Gather | agent (loc) | agent | agent |
| Validate Schema | master | master | master |
| Stage 4 | master (pytest) | **master (Ingest)** | **master (Callback)** |

`Ingest`(Grafana)와 `Callback`(Portal)은 망 분리 정책에 따라 **master에서 실행**.

## cron 인벤토리 (rule 28 #5)

각 Jenkinsfile의 `triggers` 블록 — 실 환경 (Jenkins controller)에서 측정. 본 catalog에 갱신 시 사용자 명시 승인 (rule 80 + 92 R5).

## callback URL (rule 31)

Jenkinsfile_portal의 Stage 4 Callback이 호출자에게 결과 통지:
- 정규화: `url.strip().rstrip('/')` (commit 4ccc1d7 fix)
- Method: POST
- Body: callback_plugins/json_only.py JSON envelope (rule 20)
- 보안: URL에 user:pass 형식 금지 (path/token만, rule 60)

## 갱신 trigger (rule 28 #4 / #5)

- TTL 7-14일
- Jenkinsfile* 수정
- cron 표현식 변경 (사용자 명시 승인 필수)
- 새 Jenkinsfile 추가

## 측정 명령

```bash
grep -E "stage\s*\(" Jenkinsfile Jenkinsfile_grafana Jenkinsfile_portal
grep -E "callback_url|triggers|cron" Jenkinsfile*
```

## 정본 reference

- `Jenkinsfile`, `Jenkinsfile_grafana`, `Jenkinsfile_portal` (정본)
- `docs/01_jenkins-setup.md`, `docs/04_job-registration.md`, `docs/17_jenkins-pipeline.md`
- `.claude/ai-context/infra/convention.md`
- `docs/ai/references/jenkins/pipeline-syntax.md`

## 후속 작업 (사용자 결정)

- [x] rule 80 R1-A에 pipeline별 Stage 4 차이 명시 (cycle-006, 2026-04-27 commit `211a0c7`) — closed 2026-04-28 full-sweep
- [ ] Jenkins console에서 cron 표현식 실측 + 본 catalog 갱신
