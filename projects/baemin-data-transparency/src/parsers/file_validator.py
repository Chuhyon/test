from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB
MAX_ROW_COUNT = 100_000
ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".csv"}


@dataclass
class ValidationResult:
    valid: bool
    error: str | None = None
    file_hash: str | None = None
    file_size: int = 0


def validate_file(file_path: str | Path) -> ValidationResult:
    path = Path(file_path)

    if not path.exists():
        return ValidationResult(valid=False, error="파일을 찾을 수 없습니다")

    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return ValidationResult(
            valid=False,
            error=f"지원되지 않는 파일 형식입니다. 지원: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    file_size = path.stat().st_size
    if file_size == 0:
        return ValidationResult(valid=False, error="데이터가 없는 파일입니다")

    if file_size > MAX_FILE_SIZE_BYTES:
        return ValidationResult(
            valid=False,
            error=f"파일이 너무 큽니다 (최대 {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB)",
        )

    file_hash = _compute_hash(path)

    return ValidationResult(
        valid=True, file_hash=file_hash, file_size=file_size
    )


def detect_data_category(file_path: str | Path) -> str | None:
    path = Path(file_path)
    name_lower = path.stem.lower()

    if "정산" in name_lower or "settlement" in name_lower:
        return "settlement"
    if "매출" in name_lower or "부가세" in name_lower or "sales" in name_lower:
        return "sales"
    if "광고" in name_lower or "ad" in name_lower:
        return "ad"
    if "메뉴" in name_lower or "판매" in name_lower or "menu" in name_lower:
        return "menu"

    return None


def _compute_hash(path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()
