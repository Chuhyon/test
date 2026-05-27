import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.parsers.file_validator import validate_file, detect_data_category
from src.parsers.baemin_settlement import BaeminSettlementParser


def test_file_validation():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        f.write("정산일,주문금액,입금액\n2024-03-01,100000,80000\n")
        tmp_path = f.name

    result = validate_file(tmp_path)
    assert result.valid is True
    assert result.file_hash is not None
    assert result.file_size > 0
    print("  [PASS] file validation")

    Path(tmp_path).unlink()


def test_file_validation_bad_extension():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"dummy")
        tmp_path = f.name

    result = validate_file(tmp_path)
    assert result.valid is False
    assert "지원되지 않는" in result.error
    print("  [PASS] bad extension rejected")

    Path(tmp_path).unlink()


def test_detect_category():
    assert detect_data_category("3월_정산내역.xlsx") == "settlement"
    assert detect_data_category("매출현황_2024.csv") == "sales"
    assert detect_data_category("광고성과.xlsx") == "ad"
    assert detect_data_category("메뉴별판매.csv") == "menu"
    assert detect_data_category("unknown.csv") is None
    print("  [PASS] category detection")


def test_csv_settlement_parsing():
    csv_content = (
        "정산일,주문금액,중개이용료,결제수수료,배달비,입금액\n"
        "2024-03-01,500000,34000,12500,75000,378500\n"
        "2024-03-02,600000,40800,15000,75000,469200\n"
        "2024-03-03,450000,30600,11250,75000,333150\n"
    )

    with tempfile.NamedTemporaryFile(
        suffix=".csv", delete=False, mode="w", encoding="utf-8-sig"
    ) as f:
        f.write(csv_content)
        tmp_path = f.name

    parser = BaeminSettlementParser()
    assert parser.can_parse(tmp_path) is False  # filename doesn't contain 정산
    assert parser.can_parse("/tmp/3월_정산내역.csv") is True

    result = parser.parse(tmp_path)

    assert result.records_count == 3
    assert result.error_count == 0
    assert len(result.settlements) == 3

    first = result.settlements[0]
    from decimal import Decimal
    assert first.gross_sales == Decimal("500000")
    assert first.net_deposit == Decimal("378500")
    assert len(first.fee_items) == 3
    print("  [PASS] CSV settlement parsing")

    Path(tmp_path).unlink()


if __name__ == "__main__":
    print("Running parser tests...")
    test_file_validation()
    test_file_validation_bad_extension()
    test_detect_category()
    test_csv_settlement_parsing()
    print("All parser tests passed!")
