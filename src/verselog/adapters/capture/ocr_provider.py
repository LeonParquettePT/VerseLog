import mss
import pytesseract
from PIL import Image

from verselog.adapters.capture.ocr_parser import parse_contract_text
from verselog.core.contract import Contract
from verselog.core.ports.capture_port import CapturePort


class OCRProvider(CapturePort):
    """Classic-OCR capture: screenshot the current screen, run Tesseract, parse the result."""

    def capture(self) -> Contract:
        with mss.mss() as sct:
            shot = sct.grab(sct.monitors[0])
            image = Image.frombytes("RGB", shot.size, shot.rgb)
        raw_text = pytesseract.image_to_string(image)
        return parse_contract_text(raw_text)
