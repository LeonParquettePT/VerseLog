import io

import pytesseract
from PIL import Image

from verselog.adapters.capture.ocr_parser import ContractParseError, parse_contract_text
from verselog.adapters.capture.screenshot import take_screenshot
from verselog.core.capture_result import CaptureResult
from verselog.core.ports.capture_port import CapturePort


class OCRProvider(CapturePort):
    """Classic-OCR capture: screenshot the current screen, run Tesseract, parse the result."""

    def capture(self) -> CaptureResult:
        source_image = take_screenshot()
        image = Image.open(io.BytesIO(source_image))

        try:
            raw_text = pytesseract.image_to_string(image)
            contract = parse_contract_text(raw_text)
        except (ContractParseError, pytesseract.TesseractError, pytesseract.TesseractNotFoundError) as exc:
            # A missing tesseract binary or an OCR-engine failure is exactly
            # the kind of extraction failure the trust layer should quarantine,
            # not an uncaught crash - the source image is still worth keeping.
            return CaptureResult(contract=None, source_image=source_image, parse_error=str(exc))

        return CaptureResult(contract=contract, source_image=source_image, parse_error=None)
