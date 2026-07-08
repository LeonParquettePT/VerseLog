from verselog.core.capture_result import CaptureResult
from verselog.core.contract import Contract
from verselog.core.trust_layer import TrustLayer

VALID_CONTRACT = Contract(
    departure="Port Tressler",
    arrival="Greycat Stanton IV Production Complex-A",
    scu=6,
    reward=50250.0,
)


def _trust_layer(tmp_path):
    return TrustLayer(quarantine_dir=tmp_path / "quarantine")


def test_valid_contract_is_not_quarantined_and_gets_high_confidence(tmp_path):
    result = _trust_layer(tmp_path).process(
        CaptureResult(contract=VALID_CONTRACT, source_image=b"irrelevant")
    )

    assert result.quarantined is False
    assert result.confidence == "high"
    assert result.contract == VALID_CONTRACT
    assert result.reasons == []


def test_zero_scu_is_quarantined_with_a_reason(tmp_path):
    bad_contract = Contract(**{**vars(VALID_CONTRACT), "scu": 0})

    result = _trust_layer(tmp_path).process(
        CaptureResult(contract=bad_contract, source_image=b"the-source-image")
    )

    assert result.quarantined is True
    assert result.contract is None
    assert any("scu" in reason for reason in result.reasons)


def test_zero_reward_is_quarantined(tmp_path):
    bad_contract = Contract(**{**vars(VALID_CONTRACT), "reward": 0.0})

    result = _trust_layer(tmp_path).process(
        CaptureResult(contract=bad_contract, source_image=b"the-source-image")
    )

    assert result.quarantined is True
    assert any("reward" in reason for reason in result.reasons)


def test_parse_error_is_quarantined_without_needing_field_checks(tmp_path):
    result = _trust_layer(tmp_path).process(
        CaptureResult(contract=None, source_image=b"the-source-image", parse_error="boom")
    )

    assert result.quarantined is True
    assert result.reasons == ["boom"]


def test_quarantine_keeps_the_source_image_on_disk(tmp_path):
    quarantine_dir = tmp_path / "quarantine"
    layer = TrustLayer(quarantine_dir=quarantine_dir)

    result = layer.process(
        CaptureResult(contract=None, source_image=b"the-actual-bytes", parse_error="boom")
    )

    assert result.quarantine_path is not None
    assert result.quarantine_path.read_bytes() == b"the-actual-bytes"
    assert result.quarantine_path.parent == quarantine_dir
