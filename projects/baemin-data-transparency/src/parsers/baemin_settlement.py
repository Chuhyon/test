from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from ..models.types import (
    DataCategory,
    FeeItem,
    FeeType,
    JobStatus,
    ParseResult,
    SettlementRecord,
)
from ..privacy.masking import mask_dataframe
from .base import BaseParser

REQUIRED_COLUMNS_PATTERNS = {
    "date": ["정산일", "정산날짜", "정산기준일", "날짜", "date"],
    "gross_sales": ["주문금액", "총주문금액", "매출", "총매출", "gross"],
    "net_deposit": ["입금액", "실입금액", "정산금액", "입금예정", "net"],
}

FEE_COLUMN_MAP: dict[str, FeeType] = {
    "중개이용료": FeeType.MEDIATION_FEE_DELIVERY,
    "주문중개수수료": FeeType.MEDIATION_FEE_DELIVERY,
    "포장중개이용료": FeeType.MEDIATION_FEE_PICKUP,
    "결제수수료": FeeType.PAYMENT_FEE,
    "PG수수료": FeeType.PAYMENT_FEE,
    "배달비": FeeType.DELIVERY_FEE_OWNER,
    "배달대행비": FeeType.DELIVERY_FEE_OWNER,
    "배달팁": FeeType.DELIVERY_FEE_CUSTOMER,
    "울트라콜": FeeType.AD_ULTRA_CALL,
    "오픈리스트": FeeType.AD_OPEN_LIST,
    "광고비": FeeType.AD_OTHER,
    "가게할인": FeeType.DISCOUNT_OWNER,
    "업주쿠폰": FeeType.DISCOUNT_OWNER,
    "쿠폰부담금": FeeType.COUPON_COST,
    "포인트정산": FeeType.POINT_SETTLEMENT,
    "보전금": FeeType.ADJUSTMENT_PLUS,
    "추가정산": FeeType.ADJUSTMENT_PLUS,
    "공제금": FeeType.ADJUSTMENT_MINUS,
    "마이너스충전금": FeeType.ADJUSTMENT_MINUS,
}


class BaeminSettlementParser(BaseParser):

    def can_parse(self, file_path: str | Path) -> bool:
        path = Path(file_path)
        if path.suffix.lower() not in (".xlsx", ".xls", ".csv"):
            return False
        name = path.stem.lower()
        return any(kw in name for kw in ("정산", "settlement"))

    def parse(self, file_path: str | Path) -> ParseResult:
        import openpyxl
        import csv

        path = Path(file_path)
        result = ParseResult(
            status=JobStatus.PARSING, data_category=DataCategory.SETTLEMENT
        )

        try:
            rows, headers = self._read_file(path)
        except Exception as e:
            result.status = JobStatus.FAILED
            result.errors.append(f"파일 읽기 실패: {e}")
            return result

        col_map = self._map_columns(headers)

        if "date" not in col_map:
            result.status = JobStatus.FAILED
            result.errors.append("필수 항목이 누락되었습니다: 정산일")
            return result
        if "gross_sales" not in col_map and "net_deposit" not in col_map:
            result.status = JobStatus.FAILED
            result.errors.append("필수 항목이 누락되었습니다: 주문금액 또는 입금액")
            return result

        fee_cols = self._map_fee_columns(headers)

        for i, row in enumerate(rows):
            try:
                record = self._parse_row(row, headers, col_map, fee_cols)
                if record:
                    result.settlements.append(record)
                    result.records_count += 1
            except Exception:
                result.error_count += 1
                if result.error_count <= 10:
                    result.errors.append(f"행 {i + 2} 파싱 실패")

        total = result.records_count + result.error_count
        if total > 0 and result.error_count / total >= 0.2:
            result.status = JobStatus.FAILED
            result.errors.append(
                f"파싱 실패율이 높습니다 ({result.error_count}/{total}). "
                "파일 형식이 맞는지 확인해 주세요"
            )
        else:
            result.status = JobStatus.COMPLETED
            if result.error_count > 0:
                result.warnings.append(
                    f"일부 데이터({result.error_count}건)를 읽지 못했습니다"
                )

        return result

    def _read_file(self, path: Path) -> tuple[list[list[Any]], list[str]]:
        if path.suffix.lower() in (".xlsx", ".xls"):
            return self._read_excel(path)
        return self._read_csv(path)

    def _read_excel(self, path: Path) -> tuple[list[list[Any]], list[str]]:
        import openpyxl

        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.active
        all_rows = list(ws.iter_rows(values_only=True))
        wb.close()

        if not all_rows:
            return [], []

        headers = [str(c).strip() if c else "" for c in all_rows[0]]
        data = [list(r) for r in all_rows[1:] if any(c is not None for c in r)]
        return data, headers

    def _read_csv(self, path: Path) -> tuple[list[list[Any]], list[str]]:
        import csv

        for encoding in ("utf-8-sig", "cp949", "utf-16"):
            try:
                with open(path, encoding=encoding, newline="") as f:
                    reader = csv.reader(f)
                    all_rows = list(reader)
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        else:
            raise ValueError("파일 인코딩을 인식할 수 없습니다")

        if not all_rows:
            return [], []

        headers = [c.strip() for c in all_rows[0]]
        data = all_rows[1:]
        return data, headers

    def _map_columns(self, headers: list[str]) -> dict[str, int]:
        col_map: dict[str, int] = {}
        headers_lower = [h.lower().replace(" ", "") for h in headers]

        for field_name, patterns in REQUIRED_COLUMNS_PATTERNS.items():
            for i, h in enumerate(headers_lower):
                if any(p in h for p in patterns):
                    col_map[field_name] = i
                    break

        return col_map

    def _map_fee_columns(self, headers: list[str]) -> dict[int, FeeType]:
        fee_cols: dict[int, FeeType] = {}
        for i, h in enumerate(headers):
            h_stripped = h.strip()
            for label, fee_type in FEE_COLUMN_MAP.items():
                if label in h_stripped:
                    fee_cols[i] = fee_type
                    break
        return fee_cols

    def _parse_row(
        self,
        row: list[Any],
        headers: list[str],
        col_map: dict[str, int],
        fee_cols: dict[int, FeeType],
    ) -> SettlementRecord | None:
        settlement_date = self._parse_date(row[col_map["date"]])
        if not settlement_date:
            return None

        gross_sales = self._parse_decimal(
            row[col_map["gross_sales"]] if "gross_sales" in col_map else 0
        )
        net_deposit = self._parse_decimal(
            row[col_map["net_deposit"]] if "net_deposit" in col_map else 0
        )

        fee_items: list[FeeItem] = []
        total_fees = Decimal("0")

        for col_idx, fee_type in fee_cols.items():
            if col_idx < len(row):
                amount = self._parse_decimal(row[col_idx])
                if amount != 0:
                    fee_items.append(
                        FeeItem(
                            fee_type=fee_type,
                            amount=amount,
                            fee_label=headers[col_idx].strip(),
                        )
                    )
                    if fee_type != FeeType.ADJUSTMENT_PLUS:
                        total_fees += amount
                    else:
                        total_fees -= amount

        if gross_sales == 0 and net_deposit != 0:
            gross_sales = net_deposit + total_fees

        total_deductions = gross_sales - net_deposit if net_deposit else total_fees

        return SettlementRecord(
            settlement_date=settlement_date,
            period_start=settlement_date,
            period_end=settlement_date,
            gross_sales=gross_sales,
            total_deductions=total_deductions,
            net_deposit=net_deposit,
            fee_items=fee_items,
        )

    def _parse_date(self, value: Any) -> date | None:
        if isinstance(value, (date, datetime)):
            return value if isinstance(value, date) else value.date()
        if not value:
            return None
        s = str(value).strip()
        for fmt in ("%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d", "%Y%m%d"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return None

    def _parse_decimal(self, value: Any) -> Decimal:
        if value is None:
            return Decimal("0")
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        s = str(value).strip().replace(",", "").replace("원", "").replace(" ", "")
        if not s or s == "-":
            return Decimal("0")
        try:
            return Decimal(s)
        except InvalidOperation:
            return Decimal("0")
