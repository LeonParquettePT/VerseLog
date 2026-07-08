from dataclasses import dataclass

from verselog.core.contract import Contract


@dataclass
class CaptureResult:
    """What a CapturePort returns: either a parsed Contract, or a parse_error - never both unset."""

    contract: Contract | None
    source_image: bytes
    parse_error: str | None = None
