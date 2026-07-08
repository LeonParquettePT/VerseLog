import re

from verselog.core.contract import Contract


class ContractParseError(Exception):
    """Raised when OCR'd text doesn't match an expected contract field pattern."""


_PRIMARY_OBJECTIVES_RE = re.compile(r"Primary Objectives", re.IGNORECASE)
# Anchored on the word "Reward", not the game's ¤ currency glyph: confirmed
# against real OCR output that Tesseract does not reliably render ¤ - it's
# dropped entirely on one real contract screenshot and misread as "&" on
# another. \D*? skips whatever garbage (or nothing) OCR put in its place.
_REWARD_RE = re.compile(r"Reward\D*?([\d,]+)")
_SCU_RE = re.compile(r"\d+\s*/\s*(\d+)\s*SCU")
_ARRIVAL_RE = re.compile(r"Deliver[^.]*?to\s+([^.]+)\.")
_DEPARTURE_RE = re.compile(r"Collect[^.]*?from\s+([^.]+)\.")
# \S+ only captures a single token — if the real in-game format for a
# non-N/A availability value turns out to be multi-word (e.g. "23h 59m"),
# this will need widening. Left as-is: no real (non-"N/A") example has been
# captured yet, so guessing the multi-token shape now would be unverified.
_AVAILABILITY_RE = re.compile(r"Contract Availability\s+(\S+)")


def _clean_location_name(raw: str) -> str:
    # Real OCR output confirmed: a location name that wraps across two lines
    # in the UI (e.g. "Greycat Stanton IV Production\nComplex-A") comes
    # through with an embedded newline - collapse it to a single space so the
    # name matches cleanly against LocationReferenceStore lookups later.
    return re.sub(r"\s+", " ", raw).strip()


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

    if departure_match is None:
        raise ContractParseError("could not find a 'Collect ... from <location>.' departure line")
    if arrival_match is None:
        raise ContractParseError("could not find a 'Deliver ... to <location>.' arrival line")
    if scu_match is None:
        raise ContractParseError("could not find an 'X/Y SCU' pattern")
    if reward_match is None:
        raise ContractParseError("could not find a 'Reward <amount>' pattern")

    availability = availability_match.group(1) if availability_match else None
    remaining_time = None if availability in (None, "N/A") else availability

    try:
        scu = int(scu_match.group(1))
        reward = float(reward_match.group(1).replace(",", ""))
    except ValueError as exc:
        raise ContractParseError(f"matched SCU/reward text was not a valid number: {exc}") from exc

    return Contract(
        departure=_clean_location_name(departure_match.group(1)),
        arrival=_clean_location_name(arrival_match.group(1)),
        scu=scu,
        reward=reward,
        remaining_time=remaining_time,
    )
