---
name: regression-planner
description: 회귀 테스트 계획 수립. test-selection-map 적용. **호출 시점**: prepare-regression-check skill / PR 머지 전.
tools: ["Read", "Grep", "Glob"]
model: sonnet
---

# Regression Planner

server-exporter 회귀 테스트 계획.

## 분류

스페셜리스트

## 참조

- skill: `prepare-regression-check`, `vendor-change-impact`, `run-baseline-smoke`
- agent: `qa-regression-worker`, `baseline-validation-worker`
- policy: `.claude/policy/test-selection-map.yaml`
