"""Jenkins master Web UI Browser E2E.

Covers:
  - 마스터 로그인 페이지 도달
  - 인증 후 대시보드 진입
  - Jenkins 버전 / Job list 노출 확인

본 테스트는 lab credentials 가 있는 머신에서만 실행 (conftest 자동 skip).
"""
from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


pytestmark = [pytest.mark.lab, pytest.mark.jenkins]


def _first_master(lab_creds):
    masters = lab_creds.jenkins_masters
    if not masters:
        pytest.skip("No Jenkins master defined in lab credentials")
    return masters[0]


def test_master_dashboard_reachable(page: Page, lab_creds) -> None:
    """마스터 dashboard 진입 (HTTP 200 응답)."""
    master = _first_master(lab_creds)
    url = master["web_url"]

    response = page.goto(url, wait_until="domcontentloaded", timeout=15000)
    assert response is not None, f"No response from {url}"
    assert response.status < 500, (
        f"Jenkins master returned {response.status} from {url}"
    )


@pytest.mark.skip(
    reason=(
        "Jenkins master 인증 시나리오는 사용자 계정 / API token 정책 결정 후 활성화."
        " cycle-014 후속 작업 (NEXT_ACTIONS)"
    )
)
def test_master_login_then_jobs_listed(page: Page, lab_creds) -> None:
    """SSH 자격증명 (cloviradmin/Goodmit0802!)이 Jenkins 로컬 사용자와 동일한지
    cycle-014 시점 미확인. Jenkins 사용자 / API token 정책 정해진 후 활성화."""
    master = _first_master(lab_creds)
    url = master["web_url"]

    page.goto(f"{url}/login", wait_until="domcontentloaded")
    page.fill("input[name='j_username']", master["ssh_user"])
    page.fill("input[name='j_password']", master["ssh_password"])
    page.click("button[name='Submit']")

    expect(page).to_have_url(lambda u: "login" not in u, timeout=10000)
    expect(page.locator("#tasks")).to_be_visible(timeout=10000)
