# 업로드 기반 MVP 플로우 설계 (T016)

## 사장님 여정 (5단계)

```
[1. 회원가입/동의] → [2. 파일 업로드] → [3. 파싱/검증] → [4. 리포트 생성] → [5. 리포트 확인]
```

### Step 1: 회원가입 + 동의
- 사업자등록번호로 가게 등록
- 필수 동의 2건 + 선택 동의 (consent-draft.md 참조)
- 배민 ID/PW 입력란 없음

### Step 2: 파일 업로드
- "정산자료 업로드" 버튼
- 지원 파일: xlsx, csv (file-format-spec.md 참조)
- 드래그 앤 드롭 또는 파일 선택
- 업로드 즉시 L1 파일 검증 실행

### Step 3: 파싱 + 검증
- 자동 파일 유형 감지 (정산/매출/광고/메뉴)
- 개인정보 자동 마스킹
- L2 파싱 검증 + L3 정합성 검증
- 실패 시 사장님에게 안내 메시지

### Step 4: 리포트 생성
- 정산 계산 엔진 실행
- L4 분석 검증
- 리포트 데이터 저장

### Step 5: 리포트 확인
- 핵심 지표 5개 첫 화면에 표시
- 상세 분석은 탭/섹션으로 분리
- PDF/엑셀 다운로드 가능

## API 엔드포인트 설계

| Method | Path | 설명 |
|---|---|---|
| POST | /api/stores | 가게 등록 |
| POST | /api/consents | 동의 등록 |
| POST | /api/upload | 파일 업로드 |
| GET | /api/jobs/{job_id} | 파싱 상태 조회 |
| GET | /api/reports/{store_id}/settlement | 정산 리포트 |
| GET | /api/reports/{store_id}/ads | 광고 분석 리포트 |
| GET | /api/reports/{store_id}/menus | 메뉴 수익성 리포트 |
| GET | /api/reports/{store_id}/summary | 종합 요약 |
| GET | /api/audit-logs/{store_id} | 감사 로그 조회 |
| DELETE | /api/consents/{consent_id} | 동의 철회 |
