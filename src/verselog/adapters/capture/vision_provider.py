import json

import ollama

from verselog.adapters.capture.screenshot import take_screenshot
from verselog.core.capture_result import CaptureResult
from verselog.core.contract import Contract
from verselog.core.ports.capture_port import CapturePort

_PROMPT = (
    "You are looking at a Star Citizen contract screen. Read the Reward, "
    "Contract Availability, and Primary Objectives (pickup location, "
    "delivery location, and the SCU capacity). "
    "The Primary Objectives show a line like '0/6 SCU' - that is CURRENT/CAPACITY, "
    "so for a '0/6 SCU' line the scu value is 6, not 0. "
    "Respond with the requested JSON only."
)

_CONTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "departure": {"type": "string", "description": "the pickup location"},
        "arrival": {"type": "string", "description": "the delivery location"},
        "scu": {
            "type": "integer",
            "description": (
                "the SCU capacity: the SECOND number, after the slash, in the "
                "'X/Y SCU' pair (e.g. for '0/6 SCU' this is 6, NOT 0)"
            ),
        },
        "reward": {"type": "number", "description": "the reward amount, without the currency symbol"},
        "remaining_time": {
            "type": ["string", "null"],
            "description": "Contract Availability value, or null if it reads N/A",
        },
    },
    "required": ["departure", "arrival", "scu", "reward"],
}


def _contract_from_json(raw_json: str) -> Contract:
    data = json.loads(raw_json)
    return Contract(
        departure=data["departure"],
        arrival=data["arrival"],
        scu=int(data["scu"]),
        reward=float(data["reward"]),
        remaining_time=data.get("remaining_time"),
    )


DEFAULT_VISION_MODEL = "qwen2.5vl:3b"


class VisionProvider(CapturePort):
    """Vision-model capture via Ollama: screenshot, ask a local vision model for structured JSON."""

    def __init__(self, model: str = DEFAULT_VISION_MODEL) -> None:
        self._model = model

    def capture(self) -> CaptureResult:
        source_image = take_screenshot()

        try:
            response = ollama.chat(
                model=self._model,
                messages=[{"role": "user", "content": _PROMPT, "images": [source_image]}],
                format=_CONTRACT_SCHEMA,
                # A busy contract screen (real example confirmed: a Mercenary-type
                # contract's sidebar/UI clutter) can push the vision token count past
                # Ollama's 4096 default context window, failing the request outright.
                # Raised to fit real-world screenshots we've measured going over 4096.
                options={"temperature": 0, "num_ctx": 8192},
            )
            contract = _contract_from_json(response.message.content)
        except Exception as exc:  # Ollama unreachable, model missing, malformed JSON, etc.
            return CaptureResult(contract=None, source_image=source_image, parse_error=str(exc))

        return CaptureResult(contract=contract, source_image=source_image, parse_error=None)
