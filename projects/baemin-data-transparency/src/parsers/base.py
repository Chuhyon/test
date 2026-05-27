from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ..models.types import ParseResult


class BaseParser(ABC):
    """All platform parsers inherit from this class."""

    @abstractmethod
    def parse(self, file_path: str | Path) -> ParseResult:
        ...

    @abstractmethod
    def can_parse(self, file_path: str | Path) -> bool:
        ...
