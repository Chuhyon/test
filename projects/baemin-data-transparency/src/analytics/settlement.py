from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from ..models.types import FeeType, SettlementRecord, SettlementReport

ZERO = Decimal("0")
HUNDRED = Decimal("100")


def generate_settlement_report(
    store_id: UUID,
    records: list[SettlementRecord],
    prev_period_records: list[SettlementRecord] | None = None,
) -> SettlementReport:
    if not records:
        raise ValueError("분석할 정산 데이터가 없습니다")

    gross_sales = sum(r.gross_sales for r in records)
    total_deductions = sum(r.total_deductions for r in records)
    net_deposit = sum(r.net_deposit for r in records)

    effective_fee_rate = ZERO
    if gross_sales > 0:
        effective_fee_rate = (
            (gross_sales - net_deposit) / gross_sales * HUNDRED
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    fee_breakdown = _aggregate_fees(records)
    fee_rate_breakdown = _compute_fee_rates(fee_breakdown, gross_sales)

    warnings = _validate(gross_sales, total_deductions, net_deposit, fee_breakdown)

    period_start = min(r.period_start for r in records)
    period_end = max(r.period_end for r in records)

    mom = None
    if prev_period_records:
        mom = _month_over_month(records, prev_period_records)

    return SettlementReport(
        store_id=store_id,
        period_start=period_start,
        period_end=period_end,
        gross_sales=gross_sales,
        total_deductions=total_deductions,
        net_deposit=net_deposit,
        effective_fee_rate=effective_fee_rate,
        fee_breakdown=fee_breakdown,
        fee_rate_breakdown=fee_rate_breakdown,
        month_over_month=mom,
        warnings=warnings,
    )


def _aggregate_fees(records: list[SettlementRecord]) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for record in records:
        for item in record.fee_items:
            key = item.fee_type.value
            totals[key] = totals.get(key, ZERO) + item.amount
    return totals


def _compute_fee_rates(
    fee_breakdown: dict[str, Decimal], gross_sales: Decimal
) -> dict[str, Decimal]:
    if gross_sales <= 0:
        return {}
    return {
        k: (v / gross_sales * HUNDRED).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        for k, v in fee_breakdown.items()
    }


def _validate(
    gross_sales: Decimal,
    total_deductions: Decimal,
    net_deposit: Decimal,
    fee_breakdown: dict[str, Decimal],
) -> list[str]:
    warnings = []

    diff = abs(gross_sales - total_deductions - net_deposit)
    if diff > Decimal("100"):
        warnings.append(
            f"정산 합계가 {diff}원 차이납니다. "
            "배민 정산 기준과 소수점 반올림 차이일 수 있습니다"
        )

    if gross_sales > 0:
        rate = (gross_sales - net_deposit) / gross_sales * HUNDRED
        if rate > Decimal("50"):
            warnings.append(
                f"실질 수수료율이 {rate:.1f}%로 비정상적으로 높습니다. "
                "데이터를 확인해 주세요"
            )

    fee_sum = sum(
        v for k, v in fee_breakdown.items()
        if k != FeeType.ADJUSTMENT_PLUS.value
    ) - fee_breakdown.get(FeeType.ADJUSTMENT_PLUS.value, ZERO)

    if total_deductions > 0 and abs(fee_sum - total_deductions) > Decimal("100"):
        warnings.append("수수료 항목 합계가 총 차감액과 일치하지 않습니다")

    return warnings


def _month_over_month(
    current: list[SettlementRecord],
    previous: list[SettlementRecord],
) -> dict:
    curr_sales = sum(r.gross_sales for r in current)
    prev_sales = sum(r.gross_sales for r in previous)
    curr_deposit = sum(r.net_deposit for r in current)
    prev_deposit = sum(r.net_deposit for r in previous)

    result: dict = {}

    if prev_sales > 0:
        result["sales_change_rate"] = float(
            ((curr_sales - prev_sales) / prev_sales * HUNDRED)
            .quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        )

    if curr_sales > 0 and prev_sales > 0:
        curr_rate = (curr_sales - curr_deposit) / curr_sales * HUNDRED
        prev_rate = (prev_sales - prev_deposit) / prev_sales * HUNDRED
        result["fee_rate_change"] = float(
            (curr_rate - prev_rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        )

    return result
