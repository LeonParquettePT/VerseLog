import json
from types import SimpleNamespace

import pytest

from verselog.adapters.capture import vision_provider as vision_provider_module
from verselog.adapters.capture.vision_provider import VisionProvider, _contract_from_json


class _FakeShot:
    size = (2, 1)
    rgb = b"\x00" * (2 * 1 * 3)


class _FakeSct:
    monitors = [None, {"left": 0, "top": 0, "width": 2, "height": 1}]

    def grab(self, monitor):
        return _FakeShot()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


def _patch_screenshot(monkeypatch):
    monkeypatch.setattr(vision_provider_module.mss, "mss", lambda: _FakeSct())


def test_parses_a_well_formed_json_response():
    raw_json = json.dumps(
        {
            "departure": "Port Tressler",
            "arrival": "Greycat Stanton IV Production Complex-A",
            "scu": 6,
            "reward": 50250.0,
            "remaining_time": None,
        }
    )

    contract = _contract_from_json(raw_json)

    assert contract.departure == "Port Tressler"
    assert contract.arrival == "Greycat Stanton IV Production Complex-A"
    assert contract.scu == 6
    assert contract.reward == 50250.0
    assert contract.remaining_time is None


def test_keeps_a_real_remaining_time_value():
    raw_json = json.dumps(
        {
            "departure": "A",
            "arrival": "B",
            "scu": 1,
            "reward": 100.0,
            "remaining_time": "2h34m",
        }
    )

    contract = _contract_from_json(raw_json)

    assert contract.remaining_time == "2h34m"


def test_raises_on_missing_required_field():
    raw_json = json.dumps({"departure": "A", "arrival": "B", "scu": 1})  # no reward

    with pytest.raises(KeyError):
        _contract_from_json(raw_json)


def test_raises_on_malformed_json():
    with pytest.raises(json.JSONDecodeError):
        _contract_from_json("not valid json")


def test_capture_returns_parse_error_instead_of_raising_on_malformed_response(monkeypatch):
    _patch_screenshot(monkeypatch)
    fake_response = SimpleNamespace(message=SimpleNamespace(content="not valid json"))
    monkeypatch.setattr(vision_provider_module.ollama, "chat", lambda **kwargs: fake_response)

    result = VisionProvider().capture()

    assert result.contract is None
    assert result.parse_error is not None
    assert result.source_image  # the screenshot is still kept even though parsing failed


def test_capture_returns_a_contract_on_a_well_formed_response(monkeypatch):
    _patch_screenshot(monkeypatch)
    fake_content = json.dumps(
        {"departure": "A", "arrival": "B", "scu": 1, "reward": 100.0, "remaining_time": None}
    )
    fake_response = SimpleNamespace(message=SimpleNamespace(content=fake_content))
    monkeypatch.setattr(vision_provider_module.ollama, "chat", lambda **kwargs: fake_response)

    result = VisionProvider().capture()

    assert result.parse_error is None
    assert result.contract.departure == "A"
