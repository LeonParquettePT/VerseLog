import io

import mss
import pytesseract
from PIL import Image

from verselog.adapters.capture.ocr_parser import ContractParseError, parse_contract_text
from verselog.core.capture_result import CaptureResult
from verselog.core.ports.capture_port import CapturePort


class OCRProvider(CapturePort):
    """Classic-OCR capture: screenshot the current screen, run Tesseract, parse the result."""

    def capture(self) -> CaptureResult:
        with mss.mss() as sct:
            shot = sct.grab(sct.monitors[0])
            image = Image.frombytes("RGB", shot.size, shot.rgb)

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        source_image = buffer.getvalue()

        try:
            raw_text = pytesseract.image_to_string(image)
            contract = parse_contract_text(raw_text)
        except (ContractParseError, pytesseract.TesseractError, pytesseract.TesseractNotFoundError) as exc:
            # A missing tesseract binary or an OCR-engine failure is exactly
            # the kind of extraction failure the trust layer should quarantine,
            # not an uncaught crash - the source image is still worth keeping.
            return CaptureResult(contract=None, source_image=source_image, parse_error=str(exc))

        return CaptureResult(contract=contract, source_image=source_image, parse_error=None)
