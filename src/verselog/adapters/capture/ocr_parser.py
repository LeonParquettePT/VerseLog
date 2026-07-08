import re

from verselog.core.contract import Contract

_REWARD_RE = re.compile(r"¤\s*([\d,]+)")
_SCU_RE = re.compile(r"\d+\s*/\s*(\d+)\s*SCU")
_ARRIVAL_RE = re.compile(r"Deliver[^.]*?to\s+([^.]+)\.")
_DEPARTURE_RE = re.compile(r"Collect[^.]*?from\s+([^.]+)\.")
_AVAILABILITY_RE = re.compile(r"Contract Availability\s+(\S+)")


def parse_contract_text(raw_text: str) -> Contract:
    """Parse OCR'd contract-screen text into a Contract.

    Patterns are grounded in the one real Hauling-contract example on file
    (see contract-ui-reference.md) — other contract types may phrase their
    objectives differently and could need broader patterns later.
    """
    reward_match = _REWARD_RE.search(raw_text)
    scu_match = _SCU_RE.search(raw_text)
    arrival_match = _ARRIVAL_RE.search(raw_text)
    departure_match = _DEPARTURE_RE.search(raw_text)
    availability_match = _AVAILABILITY_RE.search(raw_text)

    availability = availability_match.group(1) if availability_match else None
    remaining_time = None if availability in (None, "N/A") else availability

    return Contract(
        departure=departure_match.group(1).strip(),
        arrival=arrival_match.group(1).strip(),
        scu=int(scu_match.group(1)),
        reward=float(reward_match.group(1).replace(",", "")),
        remaining_time=remaining_time,
    )
