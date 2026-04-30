# Coverage — users 영역 (AccountService + OS users)

## 채널

- **Redfish**: `/redfish/v1/AccountService/Accounts/{slot_id}` (BMC 사용자)
- **OS Linux**: `getent passwd` + `getent group` + `lastlog` (호스트 사용자)
- **OS Windows**: `Get-LocalUser` + `Get-LocalGroup`
- **ESXi**: pyvmomi `HostSystem.config.userAccountManager.userAccount` (ESXi 호스트 사용자)

## 표준 spec (R1)

### AccountService schema (Redfish BMC)

- `/AccountService` (root)
- `/AccountService/Accounts` (collection)
- `/AccountService/Roles` (RoleId)

### ManagerAccount 필드
- `UserName`, `Password` (write-only — gather 시 없음)
- `RoleId` enum: `Administrator` / `Operator` / `ReadOnly` (표준)
- `Enabled`, `Locked`, `PasswordChangeRequired`
- `OEM`: vendor 별 추가 권한 — Dell DMC role / HPE iLO 5 OEM privileges

### Linux passwd
- `/etc/passwd` + `/etc/group` (lastlog 별도)

### Windows
- `Get-LocalUser` (Name, Enabled, LastLogon, PasswordLastSet)
- `Get-LocalGroup` + `Get-LocalGroupMember`

## Vendor 호환성 (R2)

| Vendor | AccountService | Slot 모델 | RoleId |
|---|---|---|---|
| Dell iDRAC 9 | OK | 16 slots PATCH 방식 | OEM 추가 |
| HPE iLO 5/6 | OK | POST 방식 (신규 생성) | OEM iLO 추가 |
| Lenovo XCC | OK | POST 방식 | 표준 |
| Supermicro X11+ | OK | POST 방식 | 표준 |
| Cisco CIMC | **제한** — 일부 펌웨어 AccountService 부재 / read-only | — | — |

## 알려진 사고 (R3)

### U1 — Cisco CIMC AccountService 제한 (B15 ticket / F8 / F13)
- **증상**: Cisco CIMC 일부 펌웨어가 AccountService 응답 미지원 또는 read-only
- **현재 코드 영향**: cycle 2026-04-28 P2 account_service.yml에서 `not_supported` 분기 처리. 하지만 `data.users=[]` 인데 `sections.users='not_supported'` 가 아닌 `'success'`로 잘못 분류 될 수 있음 (B15)
- **우선**: P1 (cycle 2026-05-01 인프라 활용)

### U2 — Dell iDRAC slot 기반 PATCH
- **fix 적용됨**: cycle 2026-04-28 P2 — `account_service_provision()` 안 vendor='dell' branch ✓

### U3 — HPE/Lenovo/Supermicro POST 방식
- **fix 적용됨**: cycle 2026-04-28 P2 — POST 분기 ✓

### U4 — Locked 사용자 처리
- **fix 적용됨**: account_service_dryrun OFF default + Locked 보강 (commit b5590e1d) ✓

### U5 — recovery 자격 fallback (vault 2번째 자격)
- **fix 적용됨**: cycle 2026-04-30 try_one_account.yml + cycle 2026-05-01 _compute_final_status 401/403 강제 failed ✓

### U6 — F20: BMC vendor lockout policy
- **증상**: Dell 5회 / HPE 3회 / Lenovo 5회 fail시 source IP lockout. 우리 backoff 1초 너무 짧음
- **현재 코드 영향**: try_one_account.yml backoff 1초 — multi-account 시도시 lockout 위험
- **우선**: P2

### U7 — Linux nobody / nfsnobody 시스템 사용자 처리
- **fix 적용됨**: cycle 2026-04-29 — uid<1000 + system 사용자 skip (단 root 예외) ✓

## fix 후보 (users 영역)

### F13 — Cisco CIMC AccountService 'not_supported' 분류 (Additive)
- **현재 위치**: `redfish-gather/tasks/account_service.yml` 또는 `redfish_gather.py` account 흐름
- **변경 (Additive)**: AccountService GET 응답이 404 / 401 / read-only 시 `_sections_unsupported_fragment: ['users']` set. 기존 정상 응답 vendor 동작 유지
- **회귀**: lab Dell / HPE / Lenovo / Supermicro AccountService 정상 → 'success' 유지 / Cisco CIMC → 'not_supported'
- **우선**: P1

### F20 — backoff 5초 권장 (Additive)
- **현재 위치**: `redfish-gather/tasks/try_one_account.yml:70` `command: sleep 1`
- **변경**: `sleep 5` (BMC vendor lockout 정책 대응). 단순 변경, 영향 적음
- **회귀**: 빌드 시간 증가 (5 accounts × 5s = 25s) — Jenkins stage timeout 영향 검토
- **우선**: P2

## 우리 코드 위치

- 라이브러리: `redfish_gather.py:1794` `account_service_get` + `:1848` `account_service_provision`
- task: `redfish-gather/tasks/account_service.yml` + `try_one_account.yml`
- vault: `vault/redfish/{vendor}.yml` accounts list
- OS: `os-gather/tasks/{linux,windows}/gather_users.yml`
- ESXi: 미수집 (검토 P3)

## Sources

- [Redfish AccountService DSP2046](https://redfish.dmtf.org/schemas/DSP2046_2022.2.html)
- [HPE iLO 5 AccountService](https://github.com/HewlettPackard/ilo-rest-api-docs/blob/master/source/includes/_ilo5_accountservice.md)
- [Dell iDRAC9 AccountService](https://www.dell.com/support/manuals/en-hk/idrac9-lifecycle-controller-v4.x-series/idrac9_4.00.00.00_redfishapiguide_pub/accountservice)

## 갱신 history

- 2026-05-01: R1+R2+R3 / U1~U7 / F13 P1 / F20 P2
