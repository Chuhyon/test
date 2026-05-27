# 배민 사장님 데이터 투명화 제품

## 프로젝트 개요

배달의민족 사장님이 명시적으로 제공한 자기 가게 데이터를 정산·수수료·광고비 관점에서 분석하는 **동의 기반 데이터 투명화 제품**.

- 스크래퍼가 아님. 사장님이 직접 다운로드한 파일을 업로드하면 분석하는 구조.
- 고객 개인정보, 계정 인증정보는 수집하지 않음.
- 개별 가게 데이터는 비공개, 집계 벤치마크만 익명화 후 공개.

## 폴더 구조

```
projects/baemin-data-transparency/
├── CLAUDE.md          ← 이 파일. 세션 시작 시 반드시 읽을 것
├── docs/              ← 기획 산출물 (원칙, 동의서, 데이터 범위표 등)
├── src/               ← 소스 코드 (파서, 계산 엔진, API 등)
├── tests/             ← 테스트 코드
└── data/samples/      ← 샘플 파일 (실제 데이터 커밋 금지)
```

## 제품 원칙 (모든 세션에서 준수)

1. 배민에 자동 대량 접속하지 않고, 업로드 기반 MVP로 시작한다.
2. 사장님이 명시적으로 동의한 본인 가게 데이터만 처리한다.
3. 고객 개인정보와 계정 인증정보는 기본적으로 수집하지 않는다.
4. 개별 가게 데이터는 비공개, 집계 벤치마크는 익명화 후 공개한다.
5. 정산·수수료·광고비 설명 가능성을 제품의 핵심 가치로 둔다.

## 실행 로드맵 & 진행 상태

각 Phase는 독립된 GitHub Issue로 관리. 한 세션에서는 한 Phase만 집중.

### Phase 0: 방향 확정 (D+1 ~ D+7) → Issue #1 ✅ 완료
- [x] T001: 제품 프레임 확정 → `docs/product-principles.md`
- [x] T002: 사장님 인터뷰 후보 10명 확보 → `docs/interview-plan.md` (인터뷰 설계 완료, 실제 모집은 오프라인)
- [x] T003: 배민셀프서비스 화면/다운로드 자료 맵핑 → `docs/data-source-map.md`
- [x] T004: 메시지 원칙 수립 → `docs/messaging-guidelines.md`
**산출물:** `docs/product-principles.md`, `docs/data-source-map.md`, `docs/interview-plan.md`, `docs/messaging-guidelines.md`

### Phase 1: 법무/개인정보 설계 (D+8 ~ D+20) → Issue #2 ✅ 완료
- [x] T005: 배민 약관 리스크 메모 → `docs/legal-risk-memo.md`
- [x] T006: 개인정보 처리 범위 정의 → `docs/privacy-scope.md`
- [x] T007: 동의서 초안 작성 → `docs/consent-draft.md`
- [x] T008: 보관·삭제 정책 설계 → `docs/retention-policy.md`
- [x] T009: 리뷰 원문/이미지 취급 정책 → `docs/review-data-policy.md`
- [x] T010: 계정정보 비저장 원칙 수립 → `docs/credential-policy.md`
**산출물:** `docs/legal-risk-memo.md`, `docs/privacy-scope.md`, `docs/consent-draft.md`, `docs/retention-policy.md`, `docs/review-data-policy.md`, `docs/credential-policy.md`

### Phase 2: 데이터 설계 (D+14 ~ D+20) → Issue #3 ✅ 완료
- [x] T011: 표준 데이터 모델 설계 → `docs/data-model.md`, `src/schema/init.sql`
- [x] T012: 수수료·정산 항목 사전 작성 → `docs/data-dictionary.md`
- [x] T013: raw/parsed/clean 분리 설계 → `docs/data-layer-design.md`
- [x] T014: 데이터 품질 룰 정의 → `docs/data-quality-rules.md`
- [x] T015: 익명화/마스킹 규칙 정의 → `docs/masking-policy.md`
**산출물:** `docs/data-model.md`, `docs/data-dictionary.md`, `docs/data-layer-design.md`, `docs/data-quality-rules.md`, `docs/masking-policy.md`, `src/schema/init.sql`

### Phase 3: MVP 개발 (D+21 ~ D+35) → Issue #4 ✅ 완료
- [x] T016: 업로드 기반 MVP 플로우 설계 → `docs/mvp-flow.md`
- [x] T017: 지원 파일 유형 정의 → `docs/file-format-spec.md`
- [x] T018: 파일 파서 구현 → `src/parsers/`
- [x] T019: 정산 검증 계산 로직 → `src/analytics/settlement.py`
- [x] T020: 광고 ROI 계산 로직 → `src/analytics/ad_roi.py`
- [x] T021: 메뉴별 수익성 분석 → `src/analytics/menu_profitability.py`
- [x] T022: 사장님 리포트 화면 설계 → `docs/report-ui-spec.md`
- [x] T023: 감사 로그 구현 → `src/api/audit_log.py`
**산출물:** `src/parsers/`, `src/analytics/`, `src/privacy/`, `src/api/`, `tests/`

### Phase 4: 파일럿 검증 (D+36 ~ D+55) → Issue #5
- [ ] T024: 파일럿 가게 5~10곳 모집
- [ ] T025: 수동 업로드 온보딩 문서
- [ ] T026: 파일럿 리포트 생성
- [ ] T027: 리포트 피드백 인터뷰
- [ ] T028: 수동 운영 SOP 작성
**산출물:** `docs/onboarding-guide.md`, `docs/pilot-report-template.md`

### Phase 5-6: 자동화 검토 & 출시 준비 (D+56 ~ D+90) → Issue #6
- [ ] T029: 상용 API 후보 검토
- [ ] T030: 브라우저 내보내기 도우미 PoC
- [ ] T031: 권한·철회·삭제 기능 설계
- [ ] T032: 집계 벤치마크 설계
- [ ] T033: 배민 외 플랫폼 확장 검토
- [ ] T034: 가격/패키지 가설 수립
- [ ] T035: 출시 전 보안 점검
- [ ] T036: 공개 메시지/FAQ 작성
- [ ] T037: 베타 출시 운영 계획
**산출물:** `docs/api-comparison.md`, `docs/security-checklist.md`, `docs/beta-plan.md`

## 세션 운영 규칙

1. **세션 시작 시:** 이 파일(`CLAUDE.md`)을 먼저 읽고 현재 진행 상태를 파악한다.
2. **작업 범위:** 해당 Phase의 GitHub Issue에 적힌 업무만 수행한다.
3. **완료 표시:** 업무 완료 시 이 파일의 체크리스트를 `[x]`로 갱신하고 커밋한다.
4. **산출물 위치:** 모든 파일은 `projects/baemin-data-transparency/` 하위에만 생성한다.
5. **금지사항:** 실제 사장님 데이터, 배민 ID/PW, 세션 쿠키를 커밋하지 않는다.

## 참고 자료

| 출처 | URL |
|---|---|
| 배민 이용약관 | https://img.woowahan.com/www/biz/rule/agreement.html |
| 개인정보 보호법 제26조 | https://www.law.go.kr/LSW//lsLawLinkInfo.do?chrClsCd=010202&lsId=011357&lsJoLnkSeq=900079061&print=print |
| HYPHEN 배민 API | https://hyphen.im/product/view?seq=183 |
| 아이퀘스트 배민 매출 업로드 사례 | https://www.iquest.co.kr/notice/noticeInfo.do?seqno=44&support=N |
