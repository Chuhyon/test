import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import date
from decimal import Decimal
from uuid import uuid4

from src.models.types import FeeItem, FeeType, SettlementRecord
from src.analytics.settlement import generate_settlement_report


def test_basic_settlement_report():
    store_id = uuid4()
    records = [
        SettlementRecord(
            settlement_date=date(2024, 3, 1),
            period_start=date(2024, 3, 1),
            period_end=date(2024, 3, 31),
            gross_sales=Decimal("10000000"),
            total_deductions=Decimal("2100000"),
            net_deposit=Decimal("7900000"),
            fee_items=[
                FeeItem(fee_type=FeeType.MEDIATION_FEE_DELIVERY, amount=Decimal("680000")),
                FeeItem(fee_type=FeeType.MEDIATION_FEE_VAT, amount=Decimal("68000")),
                FeeItem(fee_type=FeeType.PAYMENT_FEE, amount=Decimal("250000")),
                FeeItem(fee_type=FeeType.DELIVERY_FEE_OWNER, amount=Decimal("850000")),
                FeeItem(fee_type=FeeType.AD_ULTRA_CALL, amount=Decimal("88000")),
                FeeItem(fee_type=FeeType.AD_OPEN_LIST, amount=Decimal("164000")),
            ],
        )
    ]

    report = generate_settlement_report(store_id, records)

    assert report.gross_sales == Decimal("10000000")
    assert report.net_deposit == Decimal("7900000")
    assert report.effective_fee_rate == Decimal("21.00")
    assert report.fee_breakdown["mediation_fee_delivery"] == Decimal("680000")
    assert report.fee_rate_breakdown["mediation_fee_delivery"] == Decimal("6.80")
    print("  [PASS] basic settlement report")


def test_settlement_warnings():
    store_id = uuid4()
    records = [
        SettlementRecord(
            settlement_date=date(2024, 3, 1),
            period_start=date(2024, 3, 1),
            period_end=date(2024, 3, 31),
            gross_sales=Decimal("1000000"),
            total_deductions=Decimal("600000"),
            net_deposit=Decimal("400000"),
            fee_items=[],
        )
    ]

    report = generate_settlement_report(store_id, records)
    assert report.effective_fee_rate == Decimal("60.00")
    assert any("비정상" in w for w in report.warnings)
    print("  [PASS] settlement warnings")


def test_month_over_month():
    store_id = uuid4()
    current = [
        SettlementRecord(
            settlement_date=date(2024, 3, 1),
            period_start=date(2024, 3, 1),
            period_end=date(2024, 3, 31),
            gross_sales=Decimal("12000000"),
            total_deductions=Decimal("2520000"),
            net_deposit=Decimal("9480000"),
            fee_items=[],
        )
    ]
    previous = [
        SettlementRecord(
            settlement_date=date(2024, 2, 1),
            period_start=date(2024, 2, 1),
            period_end=date(2024, 2, 29),
            gross_sales=Decimal("10000000"),
            total_deductions=Decimal("2100000"),
            net_deposit=Decimal("7900000"),
            fee_items=[],
        )
    ]

    report = generate_settlement_report(store_id, current, previous)
    assert report.month_over_month is not None
    assert report.month_over_month["sales_change_rate"] == 20.0
    print("  [PASS] month over month")


def test_empty_records():
    store_id = uuid4()
    try:
        generate_settlement_report(store_id, [])
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    print("  [PASS] empty records raises error")


if __name__ == "__main__":
    print("Running settlement tests...")
    test_basic_settlement_report()
    test_settlement_warnings()
    test_month_over_month()
    test_empty_records()
    print("All settlement tests passed!")
