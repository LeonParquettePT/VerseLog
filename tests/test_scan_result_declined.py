from verselog.core.contract import Contract
from verselog.core.scan_result import ScanResult


def test_describe_shows_the_decline_reason_and_nothing_else():
    contract = Contract(departure="Port Tressler", arrival="Ashland", scu=6, reward=50250.0)
    result = ScanResult(
        contract=contract,
        route_cost=None,
        loading_plan=None,
        declined_reason="Standing with Nine Tails is 10, at or below the risk threshold of 25.",
    )

    description = result.describe()

    assert "Port Tressler" in description
    assert "Declined:" in description
    assert "risk threshold" in description
    assert "Route:" not in description
