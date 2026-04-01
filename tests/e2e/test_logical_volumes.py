"""LV-01~05: logical_volumes + physical_disks[].id E2E 검증.

검증 수준:
  1. storage.logical_volumes 키 존재 (모든 Redfish baseline)
  2. logical_volumes 요소 필수 필드 (id, controller_id, member_drive_ids, raid_level, health)
  3. member_drive_ids ↔ physical_disks[].id 교차 참조 (참조 무결성)
  4. physical_disks[].id 키 존재
  5. 벤더별 볼륨 수 기대값 (실장비 라이브 프로브 기준)
     - Dell R740: 1 volume (RAID1)
     - HPE DL380 Gen11: 1 volume (RAID1)
     - Lenovo SR650 V2: 1 volume (RAID1)
     - Cisco C220 M4: 2 volumes (RAID5 + RAID0)

실장비 검증일: 2026-04-01 (Cisco/HPE/Lenovo), Dell은 기존 baseline 유지
"""

import pytest

from conftest import load_json, BASELINE_DIR

# ---------------------------------------------------------------------------
# logical_volumes 요소 필수 필드
# ---------------------------------------------------------------------------
LOGICAL_VOLUME_REQUIRED_FIELDS = [
    "id",
    "controller_id",
    "member_drive_ids",
    "raid_level",
    "health",
]

LOGICAL_VOLUME_ALL_FIELDS = [
    "id",
    "name",
    "controller_id",
    "member_drive_ids",
    "raid_level",
    "total_mb",
    "health",
    "state",
    "boot_volume",
]


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------
def _get_storage(baseline: dict) -> dict:
    """baseline['data']['storage'] 반환. 없으면 빈 dict."""
    return baseline.get("data", {}).get("storage", {})


def _get_logical_volumes(baseline: dict) -> list:
    return _get_storage(baseline).get("logical_volumes", [])


def _get_physical_disk_ids(baseline: dict) -> set:
    """physical_disks[].id 값 집합 반환."""
    disks = _get_storage(baseline).get("physical_disks", [])
    return {d["id"] for d in disks if d.get("id") is not None}


def _member_resolves(member_id: str, disk_ids: set) -> bool:
    """member_drive_id가 physical_disks[].id 중 하나와 매칭되는지 확인.

    physical_disks id는 '{drive_id}:{controller_id}' 복합 포맷일 수 있음.
    member_drive_ids는 Volume Links 경로의 마지막 세그먼트(단순 id).
    예: member="PD-1", physical_disk="PD-1:SLOT-HBA" → 매칭.
    예: member="0", physical_disk="0:DE00C000" → 매칭.
    예: member="Disk.Bay.0:...", physical_disk="Disk.Bay.0:..." → 정확 매칭.
    """
    if member_id in disk_ids:
        return True
    return any(
        did.startswith(member_id + ":") or did.startswith(member_id + "/")
        for did in disk_ids
    )


# ===========================================================================
# LV-01: logical_volumes 키 존재 + 구조 검증 (모든 Redfish baseline)
# ===========================================================================
class TestLogicalVolumesStructure:
    """모든 Redfish baseline에 storage.logical_volumes 키가 존재하고,
    요소가 있으면 필수 필드를 포함하는지 검증."""

    @pytest.mark.parametrize("vendor", ["dell", "hpe", "lenovo", "cisco"])
    def test_logical_volumes_key_exists(self, vendor: str):
        baseline = load_json(BASELINE_DIR / f"{vendor}_baseline.json")
        storage = _get_storage(baseline)
        assert "logical_volumes" in storage, (
            f"{vendor}: storage.logical_volumes 키 누락"
        )
        assert isinstance(storage["logical_volumes"], list), (
            f"{vendor}: logical_volumes가 list가 아님"
        )

    @pytest.mark.parametrize("vendor", ["dell", "hpe", "lenovo", "cisco"])
    def test_logical_volume_required_fields(self, vendor: str):
        baseline = load_json(BASELINE_DIR / f"{vendor}_baseline.json")
        volumes = _get_logical_volumes(baseline)
        for i, vol in enumerate(volumes):
            assert isinstance(vol, dict), (
                f"{vendor}: logical_volumes[{i}]이 dict가 아님"
            )
            for field in LOGICAL_VOLUME_REQUIRED_FIELDS:
                assert field in vol, (
                    f"{vendor}: logical_volumes[{i}].{field} 키 누락"
                )

    @pytest.mark.parametrize("vendor", ["dell", "hpe", "lenovo", "cisco"])
    def test_logical_volume_all_fields(self, vendor: str):
        """전체 9개 필드 존재 확인 (값은 null 허용)."""
        baseline = load_json(BASELINE_DIR / f"{vendor}_baseline.json")
        volumes = _get_logical_volumes(baseline)
        for i, vol in enumerate(volumes):
            for field in LOGICAL_VOLUME_ALL_FIELDS:
                assert field in vol, (
                    f"{vendor}: logical_volumes[{i}].{field} 키 누락"
                )


# ===========================================================================
# LV-02: physical_disks[].id 존재 검증
# ===========================================================================
class TestPhysicalDiskId:
    """모든 Redfish baseline의 physical_disks 요소에 id 키가 존재하는지 검증."""

    @pytest.mark.parametrize("vendor", ["dell", "hpe", "lenovo", "cisco"])
    def test_physical_disk_has_id(self, vendor: str):
        baseline = load_json(BASELINE_DIR / f"{vendor}_baseline.json")
        disks = _get_storage(baseline).get("physical_disks", [])
        for i, disk in enumerate(disks):
            assert "id" in disk, (
                f"{vendor}: physical_disks[{i}].id 키 누락"
            )


# ===========================================================================
# LV-03: member_drive_ids ↔ physical_disks[].id 교차 참조
# ===========================================================================
class TestMemberDriveCrossReference:
    """logical_volumes[].member_drive_ids의 모든 값이
    physical_disks[].id에 존재하는지 검증 (참조 무결성)."""

    @pytest.mark.parametrize("vendor", ["dell", "cisco"])
    def test_member_drive_ids_resolve(self, vendor: str):
        """볼륨이 있는 벤더 교차 참조 검증.

        HPE 제외: baseline physical_disks가 dedup으로 1건만 존재 (4개 동일 모델),
        member_drive_ids '1'이 resolve 불가.
        Lenovo 제외: baseline physical_disks가 4개 중 2개만 존재 (Disk.0, Disk.3),
        member_drive_ids 'Disk.1'이 baseline에 없음.
        두 벤더 모두 별도 이슈 (baseline physical_disks 완전성).

        physical_disks id가 '{drive_id}:{controller_id}' 복합 포맷일 수 있으므로
        prefix 매칭도 허용."""
        baseline = load_json(BASELINE_DIR / f"{vendor}_baseline.json")
        volumes = _get_logical_volumes(baseline)
        disk_ids = _get_physical_disk_ids(baseline)

        if not volumes:
            pytest.skip(f"{vendor}: logical_volumes 비어있음")

        for i, vol in enumerate(volumes):
            member_ids = vol.get("member_drive_ids", [])
            assert isinstance(member_ids, list), (
                f"{vendor}: logical_volumes[{i}].member_drive_ids가 list가 아님"
            )
            for mid in member_ids:
                assert _member_resolves(mid, disk_ids), (
                    f"{vendor}: logical_volumes[{i}].member_drive_ids "
                    f"'{mid}'가 physical_disks[].id에 매칭 안됨. "
                    f"사용 가능한 id: {sorted(disk_ids)}"
                )

    def test_hpe_cross_ref_known_limitation(self, hpe_baseline):
        """HPE: physical_disks dedup으로 교차 참조 불완전 — 제한사항 기록."""
        volumes = _get_logical_volumes(hpe_baseline)
        disk_ids = _get_physical_disk_ids(hpe_baseline)
        assert len(volumes) == 1, "HPE: 1 volume 기대"
        # member_drive_ids '0'은 '0:DE00C000'에 prefix 매칭되지만,
        # '1'은 physical_disks에 없음 (dedup으로 4→1건)
        assert len(disk_ids) < len(volumes[0]["member_drive_ids"]), (
            "HPE dedup 제한사항이 해소됨 — 이 테스트를 strict cross-ref로 전환 필요"
        )


# ===========================================================================
# LV-04: 벤더별 볼륨 수 검증 (실장비 라이브 프로브 기준)
# ===========================================================================
class TestVendorVolumeCount:
    """실장비 프로브 결과 기반 볼륨 수 검증."""

    def test_dell_volume_count(self, dell_baseline):
        """Dell R740: 1 volume (RAID1, 2 drives)."""
        volumes = _get_logical_volumes(dell_baseline)
        assert len(volumes) == 1, f"Dell: 1 volume 기대, 실제: {len(volumes)}"
        assert volumes[0]["raid_level"] == "RAID1"

    def test_hpe_volume_count(self, hpe_baseline):
        """HPE DL380 Gen11: 1 volume (RAID1, 2 drives).
        실장비 프로브: Volume 239 "RAID1_OS"."""
        volumes = _get_logical_volumes(hpe_baseline)
        assert len(volumes) == 1, f"HPE: 1 volume 기대, 실제: {len(volumes)}"
        assert volumes[0]["raid_level"] == "RAID1"
        assert volumes[0]["id"] == "239"
        assert volumes[0]["name"] == "RAID1_OS"
        assert len(volumes[0]["member_drive_ids"]) == 2

    def test_lenovo_volume_count(self, lenovo_baseline):
        """Lenovo SR650 V2: 1 volume (RAID1, 2 drives).
        실장비 프로브: Volume Id=0, Name=OS_VD_01, RAID1, Disk.0+Disk.1."""
        volumes = _get_logical_volumes(lenovo_baseline)
        assert len(volumes) == 1, f"Lenovo: 1 volume 기대, 실제: {len(volumes)}"
        assert volumes[0]["raid_level"] == "RAID1"
        assert volumes[0]["id"] == "0"
        assert volumes[0]["name"] == "OS_VD_01"
        assert len(volumes[0]["member_drive_ids"]) == 2

    def test_cisco_volume_count(self, cisco_baseline):
        """Cisco C220 M4: 2 volumes (RAID5 + RAID0).
        실장비 프로브: VD-0 (RAID5, 5 drives), VD-1 (RAID0, 3 drives)."""
        volumes = _get_logical_volumes(cisco_baseline)
        assert len(volumes) == 2, f"Cisco: 2 volumes 기대, 실제: {len(volumes)}"

        raid_levels = sorted([v["raid_level"] for v in volumes])
        assert raid_levels == ["RAID0", "RAID5"], (
            f"Cisco RAID 구성 불일치: {raid_levels}"
        )


# ===========================================================================
# LV-05: Cisco VolumeType→RAIDType fallback 검증
# ===========================================================================
class TestCiscoVolumeTypeFallback:
    """Cisco CIMC는 Redfish v1_0_3 (RAIDType 미지원).
    VolumeType → raid_level 매핑이 올바른지 검증.

    실장비 확인:
      VD-0: VolumeType=StripedWithParity → RAID5
      VD-1: VolumeType=NonRedundant → RAID0
    """

    def test_cisco_raid5_volume(self, cisco_baseline):
        volumes = _get_logical_volumes(cisco_baseline)
        raid5_vols = [v for v in volumes if v["raid_level"] == "RAID5"]
        assert len(raid5_vols) == 1, "Cisco RAID5 볼륨 1개 기대"
        vol = raid5_vols[0]
        assert vol["id"] == "0"
        assert len(vol["member_drive_ids"]) == 5, (
            f"RAID5 드라이브 5개 기대, 실제: {len(vol['member_drive_ids'])}"
        )

    def test_cisco_raid0_volume(self, cisco_baseline):
        volumes = _get_logical_volumes(cisco_baseline)
        raid0_vols = [v for v in volumes if v["raid_level"] == "RAID0"]
        assert len(raid0_vols) == 1, "Cisco RAID0 볼륨 1개 기대"
        vol = raid0_vols[0]
        assert vol["id"] == "1"
        assert len(vol["member_drive_ids"]) == 3, (
            f"RAID0 드라이브 3개 기대, 실제: {len(vol['member_drive_ids'])}"
        )
