import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from verselog.core.capture_result import CaptureResult
from verselog.core.contract import Contract

# Placeholder heuristic: no real Star Citizen station database exists yet
# (arrives in Epic 2 Story 2.1). This only catches obviously-garbled OCR
# output (empty/near-empty strings, stray symbols) - it does NOT verify a
# station actually exists in-game. Replace once real location data lands.
_STATION_NAME_RE = re.compile(r"^[A-Za-z0-9 '\-]{3,}$")


def looks_like_a_station_name(name: str) -> bool:
    return bool(_STATION_NAME_RE.match(name.strip()))


@dataclass
class TrustResult:
    contract: Contract | None
    confidence: str | None
    quarantined: bool
    quarantine_path: Path | None
    reasons: list[str] = field(default_factory=list)


class TrustLayer:
    """The single service every CaptureResult passes through before anything downstream sees it."""

    def __init__(self, quarantine_dir: Path = Path("data/quarantine")) -> None:
        self._quarantine_dir = quarantine_dir

    def process(self, capture_result: CaptureResult) -> TrustResult:
        if capture_result.parse_error is not None or capture_result.contract is None:
            reason = capture_result.parse_error or "no contract was extracted"
            return self._quarantine(capture_result, [reason])

        reasons = self._validate(capture_result.contract)
        if reasons:
            return self._quarantine(capture_result, reasons)

        return TrustResult(
            contract=capture_result.contract,
            confidence="high",
            quarantined=False,
            quarantine_path=None,
        )

    def _validate(self, contract: Contract) -> list[str]:
        reasons = []
        if not looks_like_a_station_name(contract.departure):
            reasons.append(f"departure does not look like a station name: {contract.departure!r}")
        if not looks_like_a_station_name(contract.arrival):
            reasons.append(f"arrival does not look like a station name: {contract.arrival!r}")
        if contract.scu <= 0:
            reasons.append(f"scu must be positive, got {contract.scu}")
        if contract.reward <= 0:
            reasons.append(f"reward must be positive, got {contract.reward}")
        return reasons

    def _quarantine(self, capture_result: CaptureResult, reasons: list[str]) -> TrustResult:
        self._quarantine_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        path = self._quarantine_dir / f"{timestamp}.png"
        path.write_bytes(capture_result.source_image)
        return TrustResult(
            contract=None,
            confidence=None,
            quarantined=True,
            quarantine_path=path,
            reasons=reasons,
        )
