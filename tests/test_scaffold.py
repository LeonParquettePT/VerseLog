from verselog.core.contract import Contract


def test_contract_round_trips_its_fields():
    contract = Contract(
        departure="Port Tressler",
        arrival="Greycat Stanton IV Production Complex-A",
        scu=6,
        reward=50250.0,
        remaining_time=None,
    )

    assert contract.departure == "Port Tressler"
    assert contract.arrival == "Greycat Stanton IV Production Complex-A"
    assert contract.scu == 6
    assert contract.reward == 50250.0
    assert contract.remaining_time is None
