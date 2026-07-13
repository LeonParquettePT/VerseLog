from dataclasses import dataclass


@dataclass
class MissingPrerequisite:
    """A third-party dependency (Tesseract, Ollama) not detected on the host machine."""

    name: str
    install_instructions: str
