import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.privacy.masking import (
    mask_value,
    mask_dataframe,
    should_delete_column,
    should_mask_column,
)


def test_phone_masking():
    assert mask_value("01012345678") is None
    assert mask_value("010-1234-5678") is None
    assert mask_value("배달 완료") == "배달 완료"
    print("  [PASS] phone masking")


def test_name_masking():
    assert mask_value("김영희", "주문자") == "김**"
    assert mask_value("이순신", "고객명") == "이**"
    assert mask_value("Park", "customer") == "Pa**"
    print("  [PASS] name masking")


def test_email_masking():
    result = mask_value("test@example.com")
    assert "te" in result and "@example.com" in result
    assert "test" not in result
    print("  [PASS] email masking")


def test_card_masking():
    assert mask_value("1234-5678-9012-3456") is None
    assert mask_value("1234567890123456") is None
    print("  [PASS] card masking")


def test_ssn_masking():
    assert mask_value("900101-1234567") is None
    print("  [PASS] SSN masking")


def test_column_detection():
    assert should_delete_column("배달주소") is True
    assert should_delete_column("요청사항") is True
    assert should_delete_column("전화번호") is True
    assert should_delete_column("주문금액") is False
    assert should_mask_column("주문자") is True
    assert should_mask_column("매출") is False
    print("  [PASS] column detection")


def test_dataframe_masking():
    headers = ["주문일", "주문금액", "주문자", "전화번호", "주소", "메뉴"]
    rows = [
        ["2024-03-01", 25000, "김영희", "01012345678", "서울시 강남구 역삼동", "치킨"],
        ["2024-03-02", 18000, "이철수", "01098765432", "서울시 서초구 반포동", "피자"],
    ]

    new_headers, new_rows = mask_dataframe(headers, rows)

    assert "주소" not in new_headers
    assert "전화번호" not in new_headers
    assert "주문일" in new_headers
    assert "주문금액" in new_headers
    assert "메뉴" in new_headers

    name_idx = new_headers.index("주문자")
    assert new_rows[0][name_idx] == "김**"
    assert new_rows[1][name_idx] == "이**"
    print("  [PASS] dataframe masking")


if __name__ == "__main__":
    print("Running masking tests...")
    test_phone_masking()
    test_name_masking()
    test_email_masking()
    test_card_masking()
    test_ssn_masking()
    test_column_detection()
    test_dataframe_masking()
    print("All masking tests passed!")
