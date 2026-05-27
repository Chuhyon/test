from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from ..models.types import MenuProfitabilityReport, MenuRecord

ZERO = Decimal("0")
HUNDRED = Decimal("100")


def generate_menu_report(
    store_id: UUID,
    menus: list[MenuRecord],
    period_start=None,
    period_end=None,
) -> MenuProfitabilityReport:
    if not menus:
        raise ValueError("분석할 메뉴 데이터가 없습니다")

    menu_items = []
    for m in menus:
        revenue = m.total_revenue or (m.price * (m.total_sold or 0))
        item: dict = {
            "menu_name": m.menu_name,
            "price": float(m.price),
            "category": m.category,
            "total_sold": m.total_sold or 0,
            "revenue": float(revenue),
        }
        if m.cost is not None and m.cost > 0:
            margin = m.price - m.cost
            margin_rate = (margin / m.price * HUNDRED).quantize(
                Decimal("0.1"), rounding=ROUND_HALF_UP
            )
            total_profit = margin * (m.total_sold or 0)
            item["cost"] = float(m.cost)
            item["margin"] = float(margin)
            item["margin_rate"] = float(margin_rate)
            item["total_profit"] = float(total_profit)
        menu_items.append(item)

    top_revenue = sorted(menu_items, key=lambda x: x["revenue"], reverse=True)[:5]

    low_margin = [
        m for m in menu_items
        if "margin_rate" in m and m["margin_rate"] < 30
    ]
    low_margin.sort(key=lambda x: x.get("margin_rate", 0))

    warnings = _validate(menu_items)

    return MenuProfitabilityReport(
        store_id=store_id,
        period_start=period_start,
        period_end=period_end,
        menus=menu_items,
        top_revenue_menus=top_revenue,
        low_margin_menus=low_margin[:5],
        warnings=warnings,
    )


def _validate(menu_items: list[dict]) -> list[str]:
    warnings = []

    negative_margin = [m for m in menu_items if m.get("margin", 1) < 0]
    if negative_margin:
        names = ", ".join(m["menu_name"] for m in negative_margin[:3])
        warnings.append(f"원가가 판매가보다 높은 메뉴가 있습니다: {names}")

    no_cost = [m for m in menu_items if "cost" not in m]
    if no_cost:
        warnings.append(
            f"원가가 입력되지 않은 메뉴가 {len(no_cost)}개 있습니다. "
            "원가를 입력하면 수익성 분석이 가능합니다"
        )

    return warnings
