import ollama
import pytesseract

from verselog.adapters.capture.vision_provider import DEFAULT_VISION_MODEL
from verselog.core.missing_prerequisite import MissingPrerequisite

_TESSERACT_INSTALL_URL = "https://github.com/UB-Mannheim/tesseract/wiki"
_OLLAMA_INSTALL_URL = "https://ollama.com/download"


class PrerequisiteChecker:
    """Detects whether Tesseract, Ollama, and Ollama's vision model are ready, without installing anything."""

    def check_missing(self) -> list[MissingPrerequisite]:
        missing = []
        if not self._tesseract_available():
            missing.append(MissingPrerequisite(name="Tesseract OCR", install_instructions=_TESSERACT_INSTALL_URL))

        ollama_models = self._ollama_models()
        if ollama_models is None:
            missing.append(MissingPrerequisite(name="Ollama", install_instructions=_OLLAMA_INSTALL_URL))
        elif DEFAULT_VISION_MODEL not in ollama_models:
            missing.append(
                MissingPrerequisite(
                    name=f"Ollama vision model ({DEFAULT_VISION_MODEL})",
                    install_instructions=f"ollama pull {DEFAULT_VISION_MODEL}",
                )
            )
        return missing

    def _tesseract_available(self) -> bool:
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def _ollama_models(self) -> set[str] | None:
        try:
            response = ollama.list()
            return {model.model for model in response.models}
        except Exception:
            return None
