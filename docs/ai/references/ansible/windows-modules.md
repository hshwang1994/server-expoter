# Ansible.Windows Collection — 핵심 reference

> Source: https://docs.ansible.com/ansible/latest/collections/ansible/windows/index.html
> Fetched: 2026-04-27
> Collection version (server-exporter 검증 기준): ansible.windows 3.3.0

server-exporter os-gather Windows Play3에서 사용.

## Command Execution

| Module | 용도 | 비고 |
|---|---|---|
| `win_command` | 셸 처리 없이 명령 직접 (Windows .exe 실행) | 가장 권장 — 예측 가능 |
| `win_shell` | cmd.exe로 셸 처리 (pipe / redirect) | shell 기능 필요 시 |
| `win_powershell` | PowerShell 스크립트 직접 실행 | WMI / Registry / .NET 접근 |

**server-exporter 패턴**: Windows fact는 주로 `win_powershell`로 WMI 쿼리.

## System Info

| Module | 용도 | 핵심 데이터 |
|---|---|---|
| `setup` (Windows) | Windows facts (OS / hostname / network / hardware) | ansible_os_family / ansible_kernel / ansible_architecture / ansible_memtotal_mb / ansible_processor_* |
| `win_service_info` | Windows 서비스 list | name / display_name / state / start_mode |
| `win_product_facts` | OS 제품 / 라이선스 | product_name / edition_id / install_date |
| `win_disk_facts` | 디스크 정보 | path / size / serial_number / model |

## User / Network

| Module | 용도 |
|---|---|
| `win_user` | 로컬 user 관리 (수집에서는 read-only) |
| `win_uri` | HTTP REST (Redfish 비대상 — Windows agent 자체) |
| `win_get_url` | 파일 다운로드 |

## WinRM 연결 요구사항

server-exporter Agent (10.100.64.154):
- pywinrm 0.5.0 설치 필수
- 인증: NTLM (도메인) 또는 Basic (로컬, HTTPS 권장)
- Port: 5985 (HTTP) 또는 5986 (HTTPS)
- 자격증명: `vault/windows.yml`의 `ansible_user` + `ansible_password`

```yaml
# os-gather Windows Play 예시 (개념)
- hosts: windows_targets
  vars:
    ansible_connection: winrm
    ansible_winrm_transport: ntlm
    ansible_user: "{{ vault_windows_user }}"
    ansible_password: "{{ vault_windows_password }}"
    ansible_winrm_server_cert_validation: ignore  # 자체 서명 시
  tasks:
    - setup:
    - win_powershell:
        script: |
          Get-WmiObject Win32_BIOS | ConvertTo-Json
      register: bios_info
```

## PyWinRM Library

- Session API: `winrm.Session('host', auth=('user', 'password'))`
- Protocol API: low-level shell lifecycle 제어
- 인증: Basic / NTLM / Kerberos / CredSSP / Certificate
- 메시지 암호화: `auto` (HTTPS 또는 NTLM/Kerberos 필수)

## Best Practices for server-exporter

1. **win_powershell 우선**: WMI 기반 hardware fact는 PowerShell이 가장 강력
2. **HTTPS 권장**: 자체 서명이면 `ansible_winrm_server_cert_validation: ignore`
3. **인코딩**: PowerShell stdout은 UTF-8 또는 UTF-16 — `ConvertTo-Json` 사용 권장
4. **Vault**: `vault/windows.yml`에서 자격증명 로드

## 적용 rule

- rule 10 (gather-core) — 모듈 선택
- rule 27 (precheck-guard-first) — 4단계 진단 (Windows: ping → 5985/5986 port → WinRM → auth)
- rule 30 (integration-redfish-vmware-os) — 외부 시스템 통합
- (cycle-011: rule 60 해제 — vault/windows.yml은 cycle-012 encrypt 운영 권장)
