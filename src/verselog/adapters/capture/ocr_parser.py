import re

from verselog.core.contract import Contract

_PRIMARY_OBJECTIVES_RE = re.compile(r"Primary Objectives", re.IGNORECASE)
_REWARD_RE = re.compile(r"¤\s*([\d,]+)")
_SCU_RE = re.compile(r"\d+\s*/\s*(\d+)\s*SCU")
_ARRIVAL_RE = re.compile(r"Deliver[^.]*?to\s+([^.]+)\.")
_DEPARTURE_RE = re.compile(r"Collect[^.]*?from\s+([^.]+)\.")
# \S+ only captures a single token — if the real in-game format for a
# non-N/A availability value turns out to be multi-word (e.g. "23h 59m"),
# this will need widening. Left as-is: no real (non-"N/A") example has been
# captured yet, so guessing the multi-token shape now would be unverified.
_AVAILABILITY_RE = re.compile(r"Contract Availability\s+(\S+)")


def parse_contract_text(raw_text: str) -> Contract:
    """Parse OCR'd contract-screen text into a Contract.

    Patterns are grounded in the one real Hauling-contract example on file
    (see contract-ui-reference.md) — other contract types may phrase their
    objectives differently and could need broader patterns later.
    """
    # The Details/flavor paragraph can itself contain words like "from" or
    # "delivering" (real example: "...picking up a shipment of Quartz from
    # Port Tressler..."). Scoping departure/arrival extraction to the text
    # after "Primary Objectives" (when that heading is present in the OCR
    # output) avoids matching a decoy span in the flavor text instead of the
    # real objective line.
    objectives_marker = _PRIMARY_OBJECTIVES_RE.search(raw_text)
    objectives_text = raw_text[objectives_marker.end():] if objectives_marker else raw_text

    reward_match = _REWARD_RE.search(raw_text)
    scu_match = _SCU_RE.search(objectives_text)
    arrival_match = _ARRIVAL_RE.search(objectives_text)
    departure_match = _DEPARTURE_RE.search(objectives_text)
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
