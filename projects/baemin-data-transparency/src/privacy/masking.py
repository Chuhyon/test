from __future__ import annotations

import re
from typing import Any

PHONE_PATTERN = re.compile(r"01[016789]\d{7,8}")
CARD_PATTERN = re.compile(r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}")
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
SSN_PATTERN = re.compile(r"\d{6}[\s-]?\d{7}")
ACCOUNT_PATTERN = re.compile(r"\d{3,6}-\d{2,6}-\d{4,8}")

DELETE_COLUMN_KEYWORDS = [
    "주소", "address", "배달지",
    "요청", "메모", "request", "memo", "note", "비고",
]

MASK_COLUMN_KEYWORDS = [
    "주문자", "고객명", "이름", "수령인", "고객",
    "customer", "name", "orderer",
]

DELETE_VALUE_COLUMN_KEYWORDS = [
    "전화", "연락처", "휴대폰", "phone", "mobile", "tel",
    "카드번호", "card",
    "계좌", "account",
]

KOREAN_NAME_PATTERN = re.compile(r"^[가-힣]{2,4}$")


def should_delete_column(col_name: str) -> bool:
    col_lower = col_name.lower().strip()
    return any(kw in col_lower for kw in DELETE_COLUMN_KEYWORDS + DELETE_VALUE_COLUMN_KEYWORDS)


def should_mask_column(col_name: str) -> bool:
    col_lower = col_name.lower().strip()
    return any(kw in col_lower for kw in MASK_COLUMN_KEYWORDS)


def mask_value(value: Any, col_name: str = "") -> Any:
    if value is None:
        return None

    s = str(value).strip()
    if not s:
        return value

    if SSN_PATTERN.search(s):
        return None

    if CARD_PATTERN.search(s):
        return None

    if ACCOUNT_PATTERN.search(s):
        return None

    if PHONE_PATTERN.search(s):
        return None

    if should_mask_column(col_name):
        if KOREAN_NAME_PATTERN.match(s):
            return s[0] + "*" * (len(s) - 1)
        if len(s) > 2:
            return s[:2] + "*" * (len(s) - 2)

    if EMAIL_PATTERN.search(s):
        return EMAIL_PATTERN.sub(_mask_email, s)

    return value


def mask_dataframe(headers: list[str], rows: list[list[Any]]) -> tuple[list[str], list[list[Any]]]:
    cols_to_delete = {i for i, h in enumerate(headers) if should_delete_column(h)}
    cols_to_mask = {i for i, h in enumerate(headers) if should_mask_column(h)}

    new_headers = [h for i, h in enumerate(headers) if i not in cols_to_delete]
    new_rows = []

    for row in rows:
        new_row = []
        for i, val in enumerate(row):
            if i in cols_to_delete:
                continue
            if i in cols_to_mask:
                new_row.append(mask_value(val, headers[i]))
            else:
                new_row.append(mask_value(val))
        new_rows.append(new_row)

    return new_headers, new_rows


def _mask_email(match: re.Match) -> str:
    email = match.group(0)
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[:2] + "*" * (len(local) - 2)
    return f"{masked_local}@{domain}"
