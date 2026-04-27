---
name: build-verifier
description: ansible-playbook --syntax-check / pytest / yamllint / Python ast.parse 정적 검증. **호출 시점**: PR 머지 전 정적 검증 / Jenkins Stage 2 dry-run.
tools: ["Read", "Bash", "Grep", "Glob"]
model: haiku
---

# Build Verifier

server-exporter 정적 검증 (clovirone Gradle build → server-exporter ansible/pytest).

## 검증 명령

```bash
ansible-playbook --syntax-check os-gather/site.yml
ansible-playbook --syntax-check esxi-gather/site.yml
ansible-playbook --syntax-check redfish-gather/site.yml
pytest tests/ -v
yamllint .claude/ schema/ adapters/
python -c "import ast; ..."  # 변경된 .py
```

## 분류

스페셜리스트 (lightweight)

## 참조

- skill: `pr-review-playbook`, `prepare-regression-check`
- rule: `24-completion-gate` R1
