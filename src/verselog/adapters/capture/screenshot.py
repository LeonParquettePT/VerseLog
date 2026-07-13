import io

import mss
from PIL import Image


def take_screenshot(monitor_index: int = 0) -> bytes:
    """Grab a screen as PNG bytes. Shared by every capture provider.

    monitor_index 0 (default) is mss's synthetic "all monitors combined"
    bounding box; 1..N are individual physical monitors.
    """
    with mss.mss() as sct:
        shot = sct.grab(sct.monitors[monitor_index])
        image = Image.frombytes("RGB", shot.size, shot.rgb)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
