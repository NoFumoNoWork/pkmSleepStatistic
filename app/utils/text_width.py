"""Visual width rules for species and nickname (max width 12)."""

from __future__ import annotations

MAX_VISUAL_WIDTH = 12


def char_visual_width(ch: str) -> int:
    if not ch:
        return 0
    code = ord(ch)
    if code <= 0x007F:
        return 1
    if 0xFF61 <= code <= 0xFF9F:
        return 1
    return 2


def text_visual_width(text: str) -> int:
    return sum(char_visual_width(c) for c in text)


def is_within_width_limit(text: str, max_width: int = MAX_VISUAL_WIDTH) -> bool:
    return text_visual_width(text) <= max_width


def truncate_to_width(text: str, max_width: int = MAX_VISUAL_WIDTH) -> str:
    width = 0
    result: list[str] = []
    for ch in text:
        w = char_visual_width(ch)
        if width + w > max_width:
            break
        width += w
        result.append(ch)
    return "".join(result)
