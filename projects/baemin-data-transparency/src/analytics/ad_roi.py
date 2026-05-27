from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from ..models.types import AdRecord, AdReport, SettlementRecord

ZERO = Decimal("0")
HUNDRED = Decimal("100")
TEN_THOUSAND = Decimal("10000")


def generate_ad_report(
    store_id: UUID,
    ad_records: list[AdRecord],
    settlement_records: list[SettlementRecord] | None = None,
) -> AdReport:
    if not ad_records:
        raise ValueError("분석할 광고 데이터가 없습니다")

    total_spend = sum(r.spend for r in ad_records)
    total_attributed_orders = sum(r.attributed_orders or 0 for r in ad_records)
    total_attributed_sales = sum(r.attributed_sales or ZERO for r in ad_records)

    period_start = min(r.period_start for r in ad_records)
    period_end = max(r.period_end for r in ad_records)

    roas = None
    spend_per_order = None
    if total_spend > 0:
        if total_attributed_sales > 0:
            roas = (total_attributed_sales / total_spend * HUNDRED).quantize(
                Decimal("0.1"), rounding=ROUND_HALF_UP
            )
        if total_attributed_orders > 0:
            spend_per_order = (total_spend / total_attributed_orders).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )

    spend_ratio = None
    if settlement_records:
        gross_sales = sum(r.gross_sales for r in settlement_records)
        if gross_sales > 0:
            spend_ratio = (total_spend / gross_sales * HUNDRED).quantize(
                Decimal("0.1"), rounding=ROUND_HALF_UP
            )

    by_ad_type = _breakdown_by_type(ad_records)

    warnings = _validate(total_spend, total_attributed_sales, spend_ratio)

    return AdReport(
        store_id=store_id,
        period_start=period_start,
        period_end=period_end,
        total_spend=total_spend,
        total_attributed_orders=total_attributed_orders,
        total_attributed_sales=total_attributed_sales,
        roas=roas,
        spend_per_order=spend_per_order,
        spend_ratio=spend_ratio,
        by_ad_type=by_ad_type,
        warnings=warnings,
    )


def _breakdown_by_type(records: list[AdRecord]) -> list[dict]:
    by_type: dict[str, dict] = {}
    for r in records:
        entry = by_type.setdefault(
            r.ad_type,
            {"ad_type": r.ad_type, "spend": ZERO, "orders": 0, "sales": ZERO},
        )
        entry["spend"] += r.spend
        entry["orders"] += r.attributed_orders or 0
        entry["sales"] += r.attributed_sales or ZERO

    result = []
    for entry in by_type.values():
        spend = entry["spend"]
        item = {
            "ad_type": entry["ad_type"],
            "spend": float(spend),
            "orders": entry["orders"],
            "sales": float(entry["sales"]),
        }
        if spend > 0 and entry["orders"] > 0:
            item["cost_per_order"] = float(
                (spend / entry["orders"]).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            )
        if spend > 0 and entry["sales"] > 0:
            item["roas"] = float(
                (entry["sales"] / spend * HUNDRED).quantize(
                    Decimal("0.1"), rounding=ROUND_HALF_UP
                )
            )
        result.append(item)

    return sorted(result, key=lambda x: x["spend"], reverse=True)


def _validate(
    total_spend: Decimal,
    total_attributed_sales: Decimal,
    spend_ratio: Decimal | None,
) -> list[str]:
    warnings = []

    if total_spend > 0 and total_attributed_sales < total_spend:
        warnings.append(
            "광고비 대비 광고 경유 매출이 낮습니다 (추정). "
            "광고 효과를 재검토하세요"
        )

    if spend_ratio and spend_ratio > Decimal("30"):
        warnings.append(
            f"광고비가 매출의 {spend_ratio}%로 매우 높습니다 (확인 필요)"
        )

    warnings.append(
        "광고 효과는 인과관계가 아닌 추정치입니다. 참고용으로 활용하세요"
    )

    return warnings
