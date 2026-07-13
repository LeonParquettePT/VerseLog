import requests

from verselog.adapters.system import prerequisite_checker as checker_module
from verselog.adapters.system.prerequisite_checker import PrerequisiteChecker


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def _models_payload(*model_names):
    return {"models": [{"name": name, "model": name} for name in model_names]}


def _checker(monkeypatch, *, tesseract_ok: bool, http_get) -> PrerequisiteChecker:
    if tesseract_ok:
        monkeypatch.setattr(checker_module.subprocess, "run", lambda *a, **k: None)
    else:

        def _raise(*a, **k):
            raise FileNotFoundError("tesseract not found")

        monkeypatch.setattr(checker_module.subprocess, "run", _raise)
    return PrerequisiteChecker(http_get=http_get)


def test_check_missing_returns_empty_list_when_both_are_available(monkeypatch):
    checker = _checker(
        monkeypatch,
        tesseract_ok=True,
        http_get=lambda *a, **k: _FakeResponse(_models_payload(checker_module.DEFAULT_VISION_MODEL)),
    )

    assert checker.check_missing() == []


def test_check_missing_reports_tesseract_when_the_binary_is_missing(monkeypatch):
    checker = _checker(
        monkeypatch,
        tesseract_ok=False,
        http_get=lambda *a, **k: _FakeResponse(_models_payload(checker_module.DEFAULT_VISION_MODEL)),
    )

    missing = checker.check_missing()

    assert len(missing) == 1
    assert missing[0].name == "Tesseract OCR"
    assert missing[0].install_instructions


def test_check_missing_reports_tesseract_when_the_binary_exits_nonzero(monkeypatch):
    import subprocess

    def _raise(*a, **k):
        raise subprocess.CalledProcessError(returncode=1, cmd=["tesseract", "--version"])

    monkeypatch.setattr(checker_module.subprocess, "run", _raise)
    checker = PrerequisiteChecker(
        http_get=lambda *a, **k: _FakeResponse(_models_payload(checker_module.DEFAULT_VISION_MODEL))
    )

    missing = checker.check_missing()

    assert missing[0].name == "Tesseract OCR"


def test_check_missing_reports_tesseract_when_the_binary_hangs(monkeypatch):
    import subprocess

    def _raise(*a, **k):
        raise subprocess.TimeoutExpired(cmd=["tesseract", "--version"], timeout=5)

    monkeypatch.setattr(checker_module.subprocess, "run", _raise)
    checker = PrerequisiteChecker(
        http_get=lambda *a, **k: _FakeResponse(_models_payload(checker_module.DEFAULT_VISION_MODEL))
    )

    missing = checker.check_missing()

    assert missing[0].name == "Tesseract OCR"


def test_check_missing_reports_ollama_when_it_is_unreachable(monkeypatch):
    def _raise(*a, **k):
        raise requests.exceptions.ConnectionError("connection refused")

    checker = _checker(monkeypatch, tesseract_ok=True, http_get=_raise)

    missing = checker.check_missing()

    assert len(missing) == 1
    assert missing[0].name == "Ollama"
    assert missing[0].install_instructions


def test_check_missing_handles_a_null_models_list_without_crashing(monkeypatch):
    # A non-standard/proxied Ollama-compatible endpoint returning valid JSON
    # with {"models": null} instead of a list must not crash the check - it's
    # a reachable server reporting zero models, which correctly implies the
    # vision model specifically is missing (not "Ollama is unreachable").
    checker = _checker(monkeypatch, tesseract_ok=True, http_get=lambda *a, **k: _FakeResponse({"models": None}))

    missing = checker.check_missing()

    assert missing[0].name == f"Ollama vision model ({checker_module.DEFAULT_VISION_MODEL})"


def test_check_missing_reports_both_when_both_are_missing(monkeypatch):
    def _raise_url(*a, **k):
        raise requests.exceptions.RequestException("unreachable")

    checker = _checker(monkeypatch, tesseract_ok=False, http_get=_raise_url)

    missing = checker.check_missing()

    names = {item.name for item in missing}
    assert names == {"Tesseract OCR", "Ollama"}


def test_check_missing_reports_the_vision_model_when_ollama_is_reachable_but_the_model_isnt_pulled(monkeypatch):
    # Raised by the project's own author during real manual testing on a
    # fresh Ubuntu VM: Ollama installed and running, but its vision model
    # not yet pulled, produced a confusing "status code 404" deep inside
    # VisionProvider instead of a plain, upfront explanation.
    checker = _checker(monkeypatch, tesseract_ok=True, http_get=lambda *a, **k: _FakeResponse(_models_payload("llama3.2:1b")))

    missing = checker.check_missing()

    assert len(missing) == 1
    assert checker_module.DEFAULT_VISION_MODEL in missing[0].name
    assert checker_module.DEFAULT_VISION_MODEL in missing[0].install_instructions


def test_default_ollama_base_url_adds_a_scheme_when_the_env_var_has_none(monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", "0.0.0.0:11434")

    assert checker_module._default_ollama_base_url() == "http://0.0.0.0:11434"


def test_default_ollama_base_url_leaves_an_explicit_scheme_untouched(monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", "https://ollama.internal:443")

    assert checker_module._default_ollama_base_url() == "https://ollama.internal:443"
