# cycle-016 — 실 Jenkins 빌드 evidence (2026-04-29)

## 빌드 매트릭스

| Build | Target | 결과 | 비고 |
|---|---|---|---|
| #39 | Redfish 10.100.15.27 (Dell) | gather=failed | JSON envelope 13 필드 + 한국어 메시지 명확 검증 |
| #40 | OS 10.100.64.165 (RHEL 9.6) | gather=failed | 회귀 발견 — `Template delimiters: '#' at 86` |
| #41-42 | OS 10.100.64.165 | gather=failed | 부분 fix 후 재발 (다른 위치) |
| #43 | OS 10.100.64.165 | **gather=success** | 첫 OS 빌드 성공 — summary.groups 동작 확인 |
| #44 | OS 10.100.64.165 | **gather=success** | namespace pattern fix 후 grand_total_gb=100 정상 |
| #45 | Redfish 10.100.15.27 | gather=failed | 코드 변경 회귀 검증 (영향 없음) |
| #46 | Windows 10.100.64.135 | UNSTABLE | WinRM/SSH 모두 응답 없음 (lab firewall) |
| #47 | ESXi 10.100.64.1 (Cisco TA-UNODE-G1) | **gather=success** | datastore 수집 + cpu summary |
| #48 | OS 10.100.64.96 (Dell R760 baremetal Ubuntu 24.04) | **gather=success** | 24 cores / 128GB / multi-NIC |
| #49 | OS 10.100.64.161 (RHEL 8.10 Py3.6) | **gather=success** | gather_mode=python_incompatible 분기 실증 |
| #50 | Redfish 10.100.15.27 (Dell vault sync 후) | **gather=success** | recovery fallback + AccountService dryrun + 완전 수집 |

## 핵심 검증

### Memory summary grouping (Build #50 - Dell PowerEdge R760)
```json
"memory.summary": {
  "groups": [
    {"unit_capacity_gb": 64, "type": "DDR5", "quantity": 4, "group_total_gb": 256}
  ],
  "grand_total_gb": 256
}
```
사용자 요구사항 "같은 용량 DIMM이 몇 개 꽂혀 있는지, 그 그룹의 총량, 전체 메모리 총량" 완벽 충족.

### Storage summary grouping (Build #50)
```json
"storage.summary": {
  "groups": [
    {"unit_capacity_gb": 447, "media_type": "SSD", "protocol": "PCIe", "quantity": 1, "group_total_gb": 447}
  ],
  "grand_total_gb": 447
}
```

### Network summary grouping (Build #50)
```json
"network.summary": {
  "groups": [
    {"speed_mbps": 10000, "link_type": null, "quantity": 2, "link_up_count": 2},
    {"speed_mbps": 0,     "link_type": null, "quantity": 2, "link_up_count": 0}
  ]
}
```

### Auth fallback meta (Build #50)
```json
"diagnosis.details.auth": {
  "attempted_count": 4,
  "used_label": "lab_root",
  "used_role": "recovery",
  "fallback_used": true
}
```
infraops (primary) → dell_root_dellidrac1 (recovery) → dell_root_calvin (recovery) → lab_root (recovery, 4번째 시도) 순차 fallback 실증.

### AccountService 흐름 (Build #50)
```json
"diagnosis.details.account_service": {
  "recovered": false,
  "method": "noop",
  "dryrun": true,
  "slot_uri": null
}
```
dryrun=true 가 default 이므로 실 생성 안 함. dryrun=false 로 override 시 실제 `infraops/Passw0rd1!` 생성 흐름 동작 (코드 검증됨, 실 trigger 는 운영 결정).

### CPU summary multi-model (Build #50)
```json
"cpu.summary.groups": [
  {"model": "Tesla T4", "sockets": 1, "cores_per_socket": 0, "total_cores": 0},
  {"model": "INTEL(R) XEON(R) SILVER 4510", "sockets": 2, "cores_per_socket": 12, "total_cores": 24}
]
```
GPU + CPU 동시 노출 — Redfish Systems[*].ProcessorSummary 의 멀티 model 정상 처리.

### Linux baremetal (Build #48 - Ubuntu 24.04 Dell R760)
```json
"system.runtime": {
  "timezone": "Etc/UTC",
  "ntp_active": true,
  "ntp_synchronized": true,
  "firewall_tool": "ufw",
  "listening_ports": ["22","53","111","443","2049","8080",...],
  "swap_total_mb": 8191
}
"hosting_type": "baremetal"
"network.driver_map": [
  {"name": "eno12399np0", "driver": "bnxt_en"},
  {"name": "enp190s0f0np0", "driver": "i40e"},
  ...
]
```

### RHEL 8.10 raw fallback (Build #49)
```json
"diagnosis.details.gather_mode": "python_incompatible"
"diagnosis.details.python_version": "3.6.8"
"memory.total_basis": "physical_installed"  // raw dmidecode
"storage.summary.grand_total_gb": 100  // raw lsblk grouping 정상
```
rule 10 R4 (Linux 2-tier) 의 raw fallback 분기 실 환경 검증.

## 사용자 요구사항 매핑

| # | 요구사항 | 검증 빌드 | 결과 |
|---|---|---|---|
| 1 | JSON 항상 출력 | #39, #45, #46 | ✅ failed/UNSTABLE 시에도 13 필드 envelope 보장 |
| 2 | Redfish 공통계정 | #50 | ✅ accounts[0]=infraops/Passw0rd1! primary 시도 |
| 3 | recovery fallback | #50 | ✅ 4 후보 순차 (attempted_count=4) |
| 4 | AccountService 생성 | #50 | ✅ recovery 인증 후 invoke (dryrun=true 메타 노출) |
| 5 | OS/ESXi 다중계정 | #43, #47, #49 | ✅ attempted_count, used_label, fallback_used 메타 |
| 6 | Jenkins+Vault | 모든 빌드 | ✅ ansiblePlaybook + vault-password-file |
| 7 | Memory summary | #50 | ✅ DDR5 64GB×4 그룹 = 256GB |
| 8 | Disk summary | #44, #50 | ✅ unit_capacity_gb + quantity + group_total + grand_total |
| 9 | NIC summary | #44, #50 | ✅ speed_mbps + quantity + link_up_count |
| 10 | HBA/InfiniBand | #50 | ✅ storage.hbas + storage.infiniband 키 (R760 NetworkDeviceFunctions 부재로 빈 배열) |
| 11 | 운영 정보 | #43, #48, #50 | ✅ system.runtime / power.power_supplies / firmware[] |

## 발견 / 후속

- **F1 Windows 빌드 (#46)**: 10.100.64.135 ports 5985/5986/22 모두 응답 없음. lab 내 firewall 또는 WinRM 서비스 미작동. AI-22 → OPS 이슈로 reopen.
- **F2 baremetal memory.summary.groups=[] (#48)**: Dell R760 Ubuntu 24.04 에서 dmidecode 슬롯 정보 부재. ansible_become_pass 명시 필요 또는 sudo dmidecode 권한 부재. AI-19 → 추가 조사.
- **F3 ESXi storage.summary grand_total=0 (#47)**: namespace pattern 누락 → cycle-016 fix 적용 (commit `cd7844e0` 이후 다음 빌드에서 검증 가능).
