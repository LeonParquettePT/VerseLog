import os
import subprocess

import requests

from verselog.adapters.capture.vision_model import DEFAULT_VISION_MODEL
from verselog.core.missing_prerequisite import MissingPrerequisite

_TESSERACT_INSTALL_URL = "https://github.com/UB-Mannheim/tesseract/wiki"
_OLLAMA_INSTALL_URL = "https://ollama.com/download"
_TESSERACT_TIMEOUT_SECONDS = 5
_REQUEST_TIMEOUT_SECONDS = 5


def _default_ollama_base_url() -> str:
    # OLLAMA_HOST is commonly documented/set as host:port with no scheme
    # (e.g. "0.0.0.0:11434") - requests would otherwise raise MissingSchema.
    host = os.environ.get("OLLAMA_HOST", "localhost:11434")
    if not host.startswith(("http://", "https://")):
        host = f"http://{host}"
    return host


class PrerequisiteChecker:
    """Detects whether Tesseract, Ollama, and Ollama's vision model are ready, without installing anything.

    Deliberately avoids importing the pytesseract/ollama client libraries -
    both pull in a heavy dependency chain (Pillow, pydantic, httpx, anyio)
    that this narrow "is it installed" check doesn't need, and that weight
    ends up bundled into verselog-installer.exe (Story 6.5) for no benefit.
    A direct subprocess call and a plain `requests.get` (already a project
    dependency, and this codebase's established convention for injectable
    HTTP calls - see CommunityAPIProvider) answer the same question without
    the ollama/pytesseract client libraries.
    """

    def __init__(self, http_get=requests.get, ollama_base_url: str | None = None) -> None:
        self._http_get = http_get
        self._ollama_base_url = ollama_base_url if ollama_base_url is not None else _default_ollama_base_url()

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
                timeout=_TESSERACT_TIMEOUT_SECONDS,
            )
            return True
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False

    def _ollama_models(self) -> set[str] | None:
        # Ollama's own API is local-only (http://localhost, no TLS listener)
        # - HTTPS here would simply fail to connect, not add any real
        # protection, since the request never leaves the machine.
        try:
            response = self._http_get(f"{self._ollama_base_url}/api/tags", timeout=_REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException:
            return None
        models = data.get("models") or []
        return {model.get("model") for model in models if isinstance(model, dict) and model.get("model")}
