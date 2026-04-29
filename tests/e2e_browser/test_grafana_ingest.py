"""Grafana ingest pipeline (Jenkinsfile_grafana) Browser E2E placeholder.

Stage 4 = Ingest 인 `Jenkinsfile_grafana` 의 결과가 Grafana 대시보드에
적재되는지 검증. cycle-014 시점에는 placeholder (Grafana endpoint 미합의).

활성화 조건:
  - Grafana URL / 대시보드 ID 사용자 합의
  - lab 자격증명에 grafana entry 추가
"""
from __future__ import annotations

import pytest


pytestmark = [pytest.mark.lab, pytest.mark.grafana]


@pytest.mark.skip(reason="Grafana endpoint pending — cycle-014 후속 NEXT_ACTIONS")
def test_grafana_ingest_panel_renders(page) -> None:
    raise NotImplementedError
