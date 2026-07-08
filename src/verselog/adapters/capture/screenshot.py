import io

import mss
from PIL import Image


def take_screenshot() -> bytes:
    """Grab the primary screen as PNG bytes. Shared by every capture provider."""
    with mss.mss() as sct:
        shot = sct.grab(sct.monitors[0])
        image = Image.frombytes("RGB", shot.size, shot.rgb)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
