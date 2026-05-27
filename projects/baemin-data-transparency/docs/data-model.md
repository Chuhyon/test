# 표준 데이터 모델 설계 (T011)

## 목적

배민뿐 아니라 향후 다른 배달 플랫폼(쿠팡이츠, 요기요 등)으로 확장 가능한
플랫폼 중립적 데이터 모델을 설계한다.

## 1. ERD 개요

```
stores ──────┬──── platform_accounts
             │
             ├──── data_import_jobs ──── raw_data
             │
             ├──── settlements ──── settlement_fee_items
             │
             ├──── orders ──── order_items
             │
             ├──── ads
             │
             ├──── menus
             │
             ├──── daily_metrics
             │
             ├──── consents
             │
             └──── audit_logs
```

## 2. 테이블 정의

### 2.1 stores (가게 기본 정보)

| 컬럼 | 타입 | 필수 | 설명 |
|---|---|---|---|
| store_id | UUID | PK | 내부 가게 식별자 |
| owner_id | UUID | FK | 사장님 계정 ID |
| store_name | VARCHAR(100) | Y | 상호명 |
| business_type | VARCHAR(50) | Y | 업종 (한식, 치킨, 카페 등) |
| region | VARCHAR(100) | N | 지역 (시/구 단위, 벤치마크용) |
| business_registration_no | VARCHAR(20) | Y | 사업자등록번호 (가게 소유권 검증용) |
| created_at | TIMESTAMP | Y | 등록일 |
| updated_at | TIMESTAMP | Y | 수정일 |

### 2.2 platform_accounts (플랫폼 연결 메타데이터)

| 컬럼 | 타입 | 필수 | 설명 |
|---|---|---|---|
| platform_account_id | UUID | PK | |
| store_id | UUID | FK | stores.store_id |
| platform | VARCHAR(20) | Y | 'baemin', 'coupangeats', 'yogiyo' 등 |
| account_ref | VARCHAR(100) | N | 플랫폼 내 가게 식별 해시 (ID/PW 아님) |
| status | VARCHAR(20) | Y | 'active', 'inactive', 'pending' |
| connected_at | TIMESTAMP | Y | 연결일 |

> **주의:** account_ref는 배민 ID/PW가 아니라, 정산 자료에서 추출한
> 가게 식별 정보의 단방향 해시값이다. 원본 복원 불가.

### 2.3 data_import_jobs (업로드/수집 작업 기록)

| 컬럼 | 타입 | 필수 | 설명 |
|---|---|---|---|
| job_id | UUID | PK | |
| store_id | UUID | FK | stores.store_id |
| platform | VARCHAR(20) | Y | 원본 플랫폼 |
| import_method | VARCHAR(20) | Y | 'upload', 'api', 'browser_export' |
| file_type | VARCHAR(20) | N | 'xlsx', 'csv', 'pdf' |
| data_category | VARCHAR(30) | Y | 'settlement', 'sales', 'ad', 'menu' |
| status | VARCHAR(20) | Y | 'pending', 'parsing', 'completed', 'failed' |
| records_count | INTEGER | N | 파싱된 레코드 수 |
| error_message | TEXT | N | 실패 시 오류 내용 |
| consent_id | UUID | FK | consents.consent_id |
| uploaded_at | TIMESTAMP | Y | 업로드 시각 |
| completed_at | TIMESTAMP | N | 처리 완료 시각 |

### 2.4 raw_data (원본 파일 메타데이터)

| 컬럼 | 타입 | 필수 | 설명 |
|---|---|---|---|
| raw_data_id | UUID | PK | |
| job_id | UUID | FK | data_import_jobs.job_id |
| file_hash | VARCHAR(64) | Y | SHA-256 해시 (중복 감지용) |
| file_size_bytes | BIGINT | Y | 파일 크기 |
| storage_path | VARCHAR(500) | Y | 암호화 스토리지 경로 |
| uploaded_at | TIMESTAMP | Y | 업로드 시각 |
| retention_until | TIMESTAMP | Y | 보관 만료일 (업로드+90일) |
| deleted_at | TIMESTAMP | N | 실제 삭제 시각 |

> 원본 파일 자체는 암호화 파일 스토리지에 저장.
> 이 테이블은 메타데이터만 관리.

### 2.5 settlements (정산 데이터)

| 컬럼 | 타입 | 필수 | 설명 |
|---|---|---|---|
| settlement_id | UUID | PK | |
| store_id | UUID | FK | stores.store_id |
| platform | VARCHAR(20) | Y | 원본 플랫폼 |
| job_id | UUID | FK | data_import_jobs.job_id |
| settlement_date | DATE | Y | 정산 기준일 |
| period_start | DATE | Y | 정산 기간 시작 |
| period_end | DATE | Y | 정산 기간 종료 |
| gross_sales | DECIMAL(15,2) | Y | 총 주문금액 |
| total_deductions | DECIMAL(15,2) | Y | 총 차감액 |
| net_deposit | DECIMAL(15,2) | Y | 실입금액 |
| effective_fee_rate | DECIMAL(5,4) | N | 실질 수수료율 (계산 필드) |
| currency | VARCHAR(3) | Y | 'KRW' |
| created_at | TIMESTAMP | Y | 레코드 생성일 |

### 2.6 settlement_fee_items (수수료/차감 항목 상세)

| 컬럼 | 타입 | 필수 | 설명 |
|---|---|---|---|
| fee_item_id | UUID | PK | |
| settlement_id | UUID | FK | settlements.settlement_id |
| fee_type | VARCHAR(50) | Y | 표준 수수료 유형 (data-dictionary 참조) |
| fee_label | VARCHAR(100) | N | 플랫폼 원본 명칭 |
| amount | DECIMAL(15,2) | Y | 차감 금액 |
| rate | DECIMAL(5,4) | N | 적용 요율 (있는 경우) |
| base_amount | DECIMAL(15,2) | N | 요율 적용 기준 금액 |
| source_row_id | VARCHAR(50) | N | 원본 파일 행 참조 |
| created_at | TIMESTAMP | Y | |

### 2.7 orders (주문 집계)

| 컬럼 | 타입 | 필수 | 설명 |
|---|---|---|---|
| order_id | UUID | PK | 내부 ID (배민 주문번호 아님) |
| store_id | UUID | FK | |
| platform | VARCHAR(20) | Y | |
| job_id | UUID | FK | |
| order_date | DATE | Y | 주문일 |
| order_time | TIME | N | 주문 시각 (시간대 분석용) |
| order_amount | DECIMAL(15,2) | Y | 주문 금액 |
| delivery_fee | DECIMAL(15,2) | N | 배달비 |
| discount_amount | DECIMAL(15,2) | N | 할인 금액 |
| order_status | VARCHAR(20) | Y | 'completed', 'cancelled', 'refunded' |
| order_type | VARCHAR(20) | N | 'delivery', 'pickup' |
| created_at | TIMESTAMP | Y | |

> 고객 정보 (이름, 전화, 주소, 요청사항)는 이 테이블에 포함하지 않는다.

### 2.8 order_items (주문 메뉴 상세)

| 컬럼 | 타입 | 필수 | 설명 |
|---|---|---|---|
| order_item_id | UUID | PK | |
| order_id | UUID | FK | orders.order_id |
| menu_name | VARCHAR(200) | Y | 메뉴명 |
| quantity | INTEGER | Y | 수량 |
| unit_price | DECIMAL(15,2) | Y | 단가 |
| total_price | DECIMAL(15,2) | Y | 합계 |

### 2.9 ads (광고비 및 성과)

| 컬럼 | 타입 | 필수 | 설명 |
|---|---|---|---|
| ad_id | UUID | PK | |
| store_id | UUID | FK | |
| platform | VARCHAR(20) | Y | |
| job_id | UUID | FK | |
| ad_type | VARCHAR(50) | Y | 'ultra_call', 'open_list', 'smart_ad' 등 |
| period_start | DATE | Y | 광고 기간 시작 |
| period_end | DATE | Y | 광고 기간 종료 |
| spend | DECIMAL(15,2) | Y | 광고비 |
| impressions | INTEGER | N | 노출수 |
| clicks | INTEGER | N | 클릭수 |
| attributed_orders | INTEGER | N | 광고 경유 주문수 (추정) |
| attributed_sales | DECIMAL(15,2) | N | 광고 경유 매출 (추정) |
| created_at | TIMESTAMP | Y | |

### 2.10 menus (메뉴 정보)

| 컬럼 | 타입 | 필수 | 설명 |
|---|---|---|---|
| menu_id | UUID | PK | |
| store_id | UUID | FK | |
| platform | VARCHAR(20) | Y | |
| menu_name | VARCHAR(200) | Y | 메뉴명 |
| price | DECIMAL(15,2) | Y | 판매 가격 |
| category | VARCHAR(50) | N | 카테고리 |
| cost | DECIMAL(15,2) | N | 원가 (사장님 직접 입력, 선택) |
| is_active | BOOLEAN | Y | 현재 판매 중 여부 |
| created_at | TIMESTAMP | Y | |
| updated_at | TIMESTAMP | Y | |

### 2.11 daily_metrics (일별 집계 지표)

| 컬럼 | 타입 | 필수 | 설명 |
|---|---|---|---|
| metric_id | UUID | PK | |
| store_id | UUID | FK | |
| platform | VARCHAR(20) | Y | |
| metric_date | DATE | Y | 기준일 |
| total_orders | INTEGER | Y | 총 주문수 |
| completed_orders | INTEGER | Y | 완료 주문수 |
| cancelled_orders | INTEGER | N | 취소 주문수 |
| gross_sales | DECIMAL(15,2) | Y | 총 매출 |
| net_sales | DECIMAL(15,2) | N | 순매출 (취소 제외) |
| ad_spend | DECIMAL(15,2) | N | 당일 광고비 |
| delivery_fee_income | DECIMAL(15,2) | N | 배달비 수입 |
| delivery_fee_expense | DECIMAL(15,2) | N | 배달비 지출 |
| created_at | TIMESTAMP | Y | |

> daily_metrics는 orders, settlements, ads에서 집계하여 생성.
> 대시보드 빠른 조회용.

### 2.12 consents (동의 기록)

| 컬럼 | 타입 | 필수 | 설명 |
|---|---|---|---|
| consent_id | UUID | PK | |
| store_id | UUID | FK | |
| owner_id | UUID | FK | |
| consent_type | VARCHAR(30) | Y | 'required_basic', 'required_settlement', 'optional_ad', 'optional_menu', 'optional_benchmark', 'optional_review' |
| allowed_scopes | TEXT | Y | 허용된 데이터 범위 (JSON) |
| purpose | VARCHAR(200) | Y | 수집 목적 |
| retention_period | VARCHAR(50) | Y | 보관기간 |
| consented_at | TIMESTAMP | Y | 동의 시각 |
| revoked_at | TIMESTAMP | N | 철회 시각 |
| revoke_reason | VARCHAR(200) | N | 철회 사유 |

### 2.13 audit_logs (감사 로그)

| 컬럼 | 타입 | 필수 | 설명 |
|---|---|---|---|
| log_id | UUID | PK | |
| actor_id | UUID | Y | 행위자 (사장님 or 시스템 or 운영자) |
| actor_type | VARCHAR(20) | Y | 'owner', 'system', 'admin' |
| store_id | UUID | N | 대상 가게 |
| action | VARCHAR(50) | Y | 'upload', 'view_report', 'download', 'delete', 'consent', 'revoke' |
| data_scope | VARCHAR(50) | N | 'settlement', 'sales', 'ad', 'menu', 'review' |
| detail | TEXT | N | 상세 설명 (JSON) |
| ip_address | VARCHAR(45) | N | 요청 IP |
| created_at | TIMESTAMP | Y | |

## 3. 인덱스 전략

| 테이블 | 인덱스 | 용도 |
|---|---|---|
| settlements | (store_id, settlement_date) | 가게별 정산 조회 |
| settlement_fee_items | (settlement_id) | 정산별 수수료 항목 |
| orders | (store_id, order_date) | 가게별 주문 조회 |
| daily_metrics | (store_id, metric_date) | 가게별 일별 지표 |
| ads | (store_id, period_start) | 가게별 광고 조회 |
| audit_logs | (store_id, created_at) | 가게별 감사 로그 |
| consents | (store_id, consent_type) | 가게별 동의 상태 |
| raw_data | (retention_until) | 보관 만료 배치 삭제 |

## 4. 플랫폼 확장 설계

모든 데이터 테이블에 `platform` 컬럼을 포함하여 플랫폼 중립성을 확보한다.

| platform 값 | 설명 |
|---|---|
| baemin | 배달의민족 |
| coupangeats | 쿠팡이츠 |
| yogiyo | 요기요 |
| ddanggyo | 땡겨요 |
| pos | POS 매출 |
| card | 카드사 매출 |

파서만 플랫폼별로 구현하면 동일한 분석 엔진과 리포트를 재사용할 수 있다.
