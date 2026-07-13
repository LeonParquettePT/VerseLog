import json
import os
import subprocess
import urllib.error
import urllib.request

from verselog.core.missing_prerequisite import MissingPrerequisite
from verselog.core.vision_model import DEFAULT_VISION_MODEL

_TESSERACT_INSTALL_URL = "https://github.com/UB-Mannheim/tesseract/wiki"
_OLLAMA_INSTALL_URL = "https://ollama.com/download"
_OLLAMA_BASE_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
_REQUEST_TIMEOUT_SECONDS = 5


class PrerequisiteChecker:
    """Detects whether Tesseract, Ollama, and Ollama's vision model are ready, without installing anything.

    Deliberately avoids importing the pytesseract/ollama client libraries -
    both pull in a heavy dependency chain (Pillow, pydantic, httpx, anyio)
    that this narrow "is it installed" check doesn't need, and that weight
    ends up bundled into verselog-installer.exe (Story 6.5) for no benefit.
    A direct subprocess call and a raw HTTP request answer the same
    question, using only the standard library - the same "avoid a new
    dependency for a single OS/network check" pattern as Story 6.3's
    PowerShell-based shortcut creation.
    """

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
            subprocess.run(
                ["tesseract", "--version"],
                capture_output=True,
                check=True,
            )
            return True
        except (OSError, subprocess.CalledProcessError):
            return False

    def _ollama_models(self) -> set[str] | None:
        # Ollama's own API is local-only (http://localhost, no TLS listener)
        # - HTTPS here would simply fail to connect, not add any real
        # protection, since the request never leaves the machine.
        try:
            with urllib.request.urlopen(
                f"{_OLLAMA_BASE_URL}/api/tags", timeout=_REQUEST_TIMEOUT_SECONDS
            ) as response:
                data = json.loads(response.read())
        except (urllib.error.URLError, OSError, json.JSONDecodeError):
            return None
        return {model["model"] for model in data.get("models", [])}
