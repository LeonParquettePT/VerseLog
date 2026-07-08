import pytest

from verselog.adapters.capture.ocr_parser import ContractParseError, parse_contract_text

# Modeled on the real contract screenshot on file (contract-ui-reference.md),
# including the Details flavor paragraph that precedes Primary Objectives.
REAL_CONTRACT_TEXT = """
Opportunity for Independent Cargo Hauler

Reward
¤50,250

Contract Availability
N/A

Contracted By
Covalex Independent Contractors

Simply complete an 'Evaluation Trial' by picking up a shipment of Quartz
from Port Tressler above microTech and successfully delivering it to a
freight elevator at Greycat Stanton IV Production Complex-A on microTech.

Primary Objectives
Collect Quartz from Port Tressler.
Deliver 0/6 SCU to Greycat Stanton IV Production Complex-A.
"""


def test_parses_departure_arrival_scu_and_reward():
    contract = parse_contract_text(REAL_CONTRACT_TEXT)

    assert contract.departure == "Port Tressler"
    assert contract.arrival == "Greycat Stanton IV Production Complex-A"
    assert contract.scu == 6
    assert contract.reward == 50250.0


def test_na_availability_maps_to_no_remaining_time():
    contract = parse_contract_text(REAL_CONTRACT_TEXT)

    assert contract.remaining_time is None


def test_a_real_availability_value_is_kept():
    text_with_timer = REAL_CONTRACT_TEXT.replace(
        "Contract Availability\nN/A", "Contract Availability\n2h34m"
    )

    contract = parse_contract_text(text_with_timer)

    assert contract.remaining_time == "2h34m"


def test_decoy_collect_from_in_flavor_text_does_not_confuse_the_parser():
    # Flavor/Details text can itself say "Collect ... from ..." for an
    # unrelated location before the real Primary Objectives section appears.
    # The parser must scope extraction to Primary Objectives, not just grab
    # the first "Collect ... from ..." span in the whole screen text.
    text_with_decoy = (
        "Collect your thoughts from the chaos of the frontier, pilot.\n\n"
        + REAL_CONTRACT_TEXT
    )

    contract = parse_contract_text(text_with_decoy)

    assert contract.departure == "Port Tressler"
    assert contract.arrival == "Greycat Stanton IV Production Complex-A"


def test_reward_parses_when_ocr_drops_or_mangles_the_currency_glyph():
    # Confirmed against real screenshots: Tesseract does not reliably render
    # the game's ¤ currency glyph - it's dropped entirely on one real
    # contract and misread as "&" on another. The parser must not depend on
    # literally seeing "¤".
    text_without_symbol = REAL_CONTRACT_TEXT.replace("¤50,250", "50,250")
    contract = parse_contract_text(text_without_symbol)
    assert contract.reward == 50250.0

    text_with_garbled_symbol = REAL_CONTRACT_TEXT.replace("¤50,250", "& 50,250")
    contract = parse_contract_text(text_with_garbled_symbol)
    assert contract.reward == 50250.0


def test_arrival_name_wrapped_across_two_lines_by_ocr_is_collapsed_to_one_line():
    # Confirmed against a real screenshot: a location name that wraps across
    # two lines in the UI comes through OCR with an embedded newline.
    text_with_wrap = REAL_CONTRACT_TEXT.replace(
        "Greycat Stanton IV Production Complex-A.",
        "Greycat Stanton IV Production\nComplex-A.",
    )

    contract = parse_contract_text(text_with_wrap)

    assert contract.arrival == "Greycat Stanton IV Production Complex-A"


def test_raises_contract_parse_error_when_scu_pattern_is_missing():
    text_without_scu = REAL_CONTRACT_TEXT.replace("Deliver 0/6 SCU to", "Deliver to")

    with pytest.raises(ContractParseError):
        parse_contract_text(text_without_scu)
