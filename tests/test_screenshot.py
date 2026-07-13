from verselog.adapters.capture import screenshot as screenshot_module
from verselog.adapters.capture.screenshot import take_screenshot


class _FakeShot:
    size = (2, 2)
    rgb = b"\x00" * (2 * 2 * 3)


class _FakeSct:
    def __init__(self):
        self.monitors = ["all", "monitor-1", "monitor-2"]
        self.grabbed_with = None

    def grab(self, monitor):
        self.grabbed_with = monitor
        return _FakeShot()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_take_screenshot_defaults_to_monitor_index_zero(monkeypatch):
    fake_sct = _FakeSct()
    monkeypatch.setattr(screenshot_module.mss, "mss", lambda: fake_sct)

    take_screenshot()

    assert fake_sct.grabbed_with == "all"


def test_take_screenshot_uses_the_given_monitor_index(monkeypatch):
    fake_sct = _FakeSct()
    monkeypatch.setattr(screenshot_module.mss, "mss", lambda: fake_sct)

    take_screenshot(monitor_index=2)

    assert fake_sct.grabbed_with == "monitor-2"
