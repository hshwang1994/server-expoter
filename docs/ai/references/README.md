# server-exporter Reference Library

> 외부 시스템 / 라이브러리 / 표준 규격 참고 문서. AI가 skills / agents / rule 작성 시 참조.
> Plan 2 시작 시점에 1차 수집 (2026-04-27).

## 구조

```
docs/ai/references/
├── ansible/
│   ├── builtin-modules.md       # ansible.builtin (setup/raw/include_tasks 등)
│   ├── windows-modules.md       # ansible.windows 3.3.0
│   └── ansible-vault.md         # Vault 명령 / 2단계 로딩
├── redfish/
│   └── redfish-spec.md          # DMTF Redfish 표준 + 벤더별 BMC 매핑
├── vmware/
│   └── community-vmware-modules.md  # community.vmware 6.2.0
├── python/
│   └── pyvmomi.md               # pyvmomi 9.0.0
└── winrm/
    └── pywinrm.md               # pywinrm 0.5.0
```

## 활용 원칙

1. **인덱스로만**: 본문은 정본 (Ansible 공식 / 벤더 BMC manual / RFC). 본 reference는 핵심 추출 + server-exporter 적용 매핑
2. **TTL 90일** (rule 28 #11 외부 계약): 분기마다 재 fetch 권장
3. **drift 감지 시 보강**: 새 펌웨어 / 새 ansible 버전 / 새 라이브러리 시 갱신
4. **skill / agent / rule 본문은 본 reference 참조**: skill 본문에 외부 정보 풀어 쓰지 말고 `docs/ai/references/...` link

## 갱신 절차

1. WebFetch로 source URL fetch
2. server-exporter 적용 매핑 추가 (어떤 rule / skill / agent와 연결되는지)
3. version 명시 (검증 기준 Agent 10.100.64.154 기준)
4. 적용 rule 명시
5. `docs/ai/catalogs/EXTERNAL_CONTRACTS.md`에 drift 발견 시 추가

## 향후 추가 예정

- DMTF Redfish OData 스키마 상세 (probe-redfish-vendor skill 보강 시)
- python-redfish / sushy 비교 (현재 stdlib 우선이라 미사용)
- jmespath 필터 패턴 (filter_plugins 작성 시)
- ansible callback plugin API (json_only.py 변경 시)
- Jinja2 템플릿 가이드 (post_edit_jinja_check 정합성 확장 시)
- Jenkins Pipeline syntax (Jenkinsfile 3종 작업 시)
