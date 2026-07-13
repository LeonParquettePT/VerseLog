from types import SimpleNamespace

from verselog.adapters.system import prerequisite_checker as checker_module
from verselog.adapters.system.prerequisite_checker import PrerequisiteChecker


def _list_response(*model_names):
    return SimpleNamespace(models=[SimpleNamespace(model=name) for name in model_names])


def test_check_missing_returns_empty_list_when_both_are_available(monkeypatch):
    monkeypatch.setattr(checker_module.pytesseract, "get_tesseract_version", lambda: "5.3.0")
    monkeypatch.setattr(checker_module.ollama, "list", lambda: _list_response(checker_module.DEFAULT_VISION_MODEL))

    assert PrerequisiteChecker().check_missing() == []


def test_check_missing_reports_tesseract_when_it_raises(monkeypatch):
    def _raise():
        raise checker_module.pytesseract.TesseractNotFoundError()

    monkeypatch.setattr(checker_module.pytesseract, "get_tesseract_version", _raise)
    monkeypatch.setattr(checker_module.ollama, "list", lambda: _list_response(checker_module.DEFAULT_VISION_MODEL))

    missing = PrerequisiteChecker().check_missing()

    assert len(missing) == 1
    assert missing[0].name == "Tesseract OCR"
    assert missing[0].install_instructions


def test_check_missing_reports_ollama_when_it_raises(monkeypatch):
    def _raise():
        raise ConnectionError("Ollama unreachable")

    monkeypatch.setattr(checker_module.pytesseract, "get_tesseract_version", lambda: "5.3.0")
    monkeypatch.setattr(checker_module.ollama, "list", _raise)

    missing = PrerequisiteChecker().check_missing()

    assert len(missing) == 1
    assert missing[0].name == "Ollama"
    assert missing[0].install_instructions


def test_check_missing_reports_both_when_both_raise(monkeypatch):
    def _raise():
        raise Exception("unavailable")

    monkeypatch.setattr(checker_module.pytesseract, "get_tesseract_version", _raise)
    monkeypatch.setattr(checker_module.ollama, "list", _raise)

    missing = PrerequisiteChecker().check_missing()

    names = {item.name for item in missing}
    assert names == {"Tesseract OCR", "Ollama"}


def test_check_missing_reports_the_vision_model_when_ollama_is_reachable_but_the_model_isnt_pulled(monkeypatch):
    # Raised by the project's own author during real manual testing on a
    # fresh Ubuntu VM: Ollama installed and running, but its vision model
    # not yet pulled, produced a confusing "status code 404" deep inside
    # VisionProvider instead of a plain, upfront explanation.
    monkeypatch.setattr(checker_module.pytesseract, "get_tesseract_version", lambda: "5.3.0")
    monkeypatch.setattr(checker_module.ollama, "list", lambda: _list_response("llama3.2:1b"))

    missing = PrerequisiteChecker().check_missing()

    assert len(missing) == 1
    assert checker_module.DEFAULT_VISION_MODEL in missing[0].name
    assert checker_module.DEFAULT_VISION_MODEL in missing[0].install_instructions
