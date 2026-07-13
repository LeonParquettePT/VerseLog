import io

from PIL import Image

from verselog.adapters.capture import ocr_provider as ocr_provider_module
from verselog.adapters.capture.ocr_provider import OCRProvider


def _tiny_png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (1, 1)).save(buffer, format="PNG")
    return buffer.getvalue()


def test_capture_passes_the_configured_monitor_index_to_take_screenshot(monkeypatch):
    seen = {}

    def _fake_take_screenshot(monitor_index=0):
        seen["index"] = monitor_index
        return _tiny_png_bytes()

    monkeypatch.setattr(ocr_provider_module, "take_screenshot", _fake_take_screenshot)
    monkeypatch.setattr(ocr_provider_module.pytesseract, "image_to_string", lambda image: "not a real contract")

    OCRProvider(monitor_index=1).capture()

    assert seen["index"] == 1


def test_capture_defaults_to_monitor_index_zero(monkeypatch):
    seen = {}

    def _fake_take_screenshot(monitor_index=0):
        seen["index"] = monitor_index
        return _tiny_png_bytes()

    monkeypatch.setattr(ocr_provider_module, "take_screenshot", _fake_take_screenshot)
    monkeypatch.setattr(ocr_provider_module.pytesseract, "image_to_string", lambda image: "not a real contract")

    OCRProvider().capture()

    assert seen["index"] == 0
