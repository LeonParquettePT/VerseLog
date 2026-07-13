import ctypes

_VISION_TIER_MIN_RAM_BYTES = 8 * 1024**3  # 8 GiB - below this, recommend the lighter OCR tier


class _MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def total_ram_bytes() -> int:
    """Real total physical RAM via the Windows API - no new pip dependency (Story 6.3's own precedent)."""
    stat = _MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(_MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    return stat.ullTotalPhys


def recommend_tier(total_ram_bytes: int, cpu_count: int) -> str:
    """A rough, prerequisite-independent guess - `verselog.exe`'s own real, timed
    benchmark (Story 1.6) always supersedes this on first real launch.
    """
    if total_ram_bytes >= _VISION_TIER_MIN_RAM_BYTES:
        return "vision"
    return "ocr"
