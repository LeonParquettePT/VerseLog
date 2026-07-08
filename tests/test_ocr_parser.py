from verselog.adapters.capture.ocr_parser import parse_contract_text

# Modeled on the real contract screenshot on file (contract-ui-reference.md)
REAL_CONTRACT_TEXT = """
Opportunity for Independent Cargo Hauler

Reward
¤50,250

Contract Availability
N/A

Contracted By
Covalex Independent Contractors

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
