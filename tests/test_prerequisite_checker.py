import json
import subprocess
import urllib.error

from verselog.adapters.system import prerequisite_checker as checker_module
from verselog.adapters.system.prerequisite_checker import PrerequisiteChecker


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._body = json.dumps(payload).encode()

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc_info) -> None:
        return None


def _models_payload(*model_names):
    return {"models": [{"name": name, "model": name} for name in model_names]}


def test_check_missing_returns_empty_list_when_both_are_available(monkeypatch):
    monkeypatch.setattr(checker_module.subprocess, "run", lambda *a, **k: None)
    monkeypatch.setattr(
        checker_module.urllib.request,
        "urlopen",
        lambda *a, **k: _FakeResponse(_models_payload(checker_module.DEFAULT_VISION_MODEL)),
    )

    assert PrerequisiteChecker().check_missing() == []


def test_check_missing_reports_tesseract_when_the_binary_is_missing(monkeypatch):
    def _raise(*a, **k):
        raise FileNotFoundError("tesseract not found")

    monkeypatch.setattr(checker_module.subprocess, "run", _raise)
    monkeypatch.setattr(
        checker_module.urllib.request,
        "urlopen",
        lambda *a, **k: _FakeResponse(_models_payload(checker_module.DEFAULT_VISION_MODEL)),
    )

    missing = PrerequisiteChecker().check_missing()

    assert len(missing) == 1
    assert missing[0].name == "Tesseract OCR"
    assert missing[0].install_instructions


def test_check_missing_reports_tesseract_when_the_binary_exits_nonzero(monkeypatch):
    def _raise(*a, **k):
        raise subprocess.CalledProcessError(returncode=1, cmd=["tesseract", "--version"])

    monkeypatch.setattr(checker_module.subprocess, "run", _raise)
    monkeypatch.setattr(
        checker_module.urllib.request,
        "urlopen",
        lambda *a, **k: _FakeResponse(_models_payload(checker_module.DEFAULT_VISION_MODEL)),
    )

    missing = PrerequisiteChecker().check_missing()

    assert missing[0].name == "Tesseract OCR"


def test_check_missing_reports_ollama_when_it_is_unreachable(monkeypatch):
    def _raise(*a, **k):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(checker_module.subprocess, "run", lambda *a, **k: None)
    monkeypatch.setattr(checker_module.urllib.request, "urlopen", _raise)

    missing = PrerequisiteChecker().check_missing()

    assert len(missing) == 1
    assert missing[0].name == "Ollama"
    assert missing[0].install_instructions


def test_check_missing_reports_both_when_both_are_missing(monkeypatch):
    def _raise_process(*a, **k):
        raise FileNotFoundError()

    def _raise_url(*a, **k):
        raise urllib.error.URLError("unreachable")

    monkeypatch.setattr(checker_module.subprocess, "run", _raise_process)
    monkeypatch.setattr(checker_module.urllib.request, "urlopen", _raise_url)

    missing = PrerequisiteChecker().check_missing()

    names = {item.name for item in missing}
    assert names == {"Tesseract OCR", "Ollama"}


def test_check_missing_reports_the_vision_model_when_ollama_is_reachable_but_the_model_isnt_pulled(monkeypatch):
    # Raised by the project's own author during real manual testing on a
    # fresh Ubuntu VM: Ollama installed and running, but its vision model
    # not yet pulled, produced a confusing "status code 404" deep inside
    # VisionProvider instead of a plain, upfront explanation.
    monkeypatch.setattr(checker_module.subprocess, "run", lambda *a, **k: None)
    monkeypatch.setattr(
        checker_module.urllib.request, "urlopen", lambda *a, **k: _FakeResponse(_models_payload("llama3.2:1b"))
    )

    missing = PrerequisiteChecker().check_missing()

    assert len(missing) == 1
    assert checker_module.DEFAULT_VISION_MODEL in missing[0].name
    assert checker_module.DEFAULT_VISION_MODEL in missing[0].install_instructions
