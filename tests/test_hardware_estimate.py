from verselog_installer.hardware_estimate import recommend_tier

_ONE_GIB = 1024**3


def test_recommend_tier_is_vision_comfortably_above_the_threshold():
    assert recommend_tier(total_ram_bytes=16 * _ONE_GIB) == "vision"


def test_recommend_tier_is_ocr_comfortably_below_the_threshold():
    assert recommend_tier(total_ram_bytes=4 * _ONE_GIB) == "ocr"


def test_recommend_tier_is_vision_exactly_at_the_threshold():
    assert recommend_tier(total_ram_bytes=8 * _ONE_GIB) == "vision"


def test_recommend_tier_is_ocr_just_below_the_threshold():
    assert recommend_tier(total_ram_bytes=8 * _ONE_GIB - 1) == "ocr"
