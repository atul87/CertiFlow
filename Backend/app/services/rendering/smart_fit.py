"""
SmartFit — P3.18–P3.22

Given a text string, a bounding box (w × h), and style parameters,
returns the rendered text (possibly line-wrapped), the applied font,
and the final font size.  Reports TEXT_OVERFLOW if the text cannot
be made to fit even at the minimum allowed size.
"""
from __future__ import annotations
import textwrap
from dataclasses import dataclass
from typing import Optional, Tuple
from PIL import ImageDraw, ImageFont
from app.services.rendering import font_manager


@dataclass
class SmartFitResult:
    lines: list[str]           # Final lines to render
    font: ImageFont.ImageFont
    font_size: int
    text_width: int            # Measured total width of widest line
    text_height: int           # Measured total height of all lines
    overflowed: bool           # True if could not fit even at min size
    overflow_detail: Optional[dict] = None


def _measure_lines(
    lines: list[str],
    font: ImageFont.ImageFont,
    draw: ImageDraw.ImageDraw,
    line_height_multiplier: float = 1.2,
) -> Tuple[int, int]:
    """Return (max_width, total_height) for a list of text lines."""
    max_w = 0
    total_h = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        max_w = max(max_w, lw)
        total_h += int(lh * line_height_multiplier)
    return max_w, total_h


def smart_fit(
    text: str,
    box_width: int,
    box_height: int,
    family: str = "Inter",
    initial_size: int = 72,
    min_size: int = 14,
    weight: int = 400,
    italic: bool = False,
    line_height: float = 1.2,
    max_lines: int = 10,
    allow_wrap: bool = True,
    allow_shrink: bool = True,
    element_id: str = "",
    field_name: str = "",
) -> SmartFitResult:
    """
    Algorithm (P3.18–P3.20):
      1. Start at initial_size.
      2. Wrap text to box_width at current size.
      3. If wrapped lines fit inside box_height  → done.
      4. If allow_shrink and size > min_size     → reduce by 2px and retry.
      5. If still not fitting at min_size        → mark overflowed=True.
    """
    # Use a dummy image draw for measurements (1x1 is fine)
    from PIL import Image
    _dummy = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(_dummy)

    size = initial_size

    while size >= min_size:
        font = font_manager.load_font(family, size, weight, italic)

        # Estimate chars per line via average char width
        sample_bbox = draw.textbbox((0, 0), "W", font=font)
        avg_char_w = max(1, sample_bbox[2] - sample_bbox[0])
        chars_per_line = max(1, int(box_width / avg_char_w))

        if allow_wrap:
            wrapped = textwrap.wrap(text, width=chars_per_line, break_long_words=True)
            if not wrapped:
                wrapped = [text]
            # Respect max_lines
            wrapped = wrapped[:max_lines]
        else:
            wrapped = [text]

        tw, th = _measure_lines(wrapped, font, draw, line_height)

        fits_width = tw <= box_width
        fits_height = th <= box_height

        if fits_width and fits_height:
            return SmartFitResult(
                lines=wrapped,
                font=font,
                font_size=size,
                text_width=tw,
                text_height=th,
                overflowed=False,
            )

        if allow_shrink and size > min_size:
            size = max(min_size, size - 2)
            continue

        # Cannot shrink further
        break

    # Still here → overflow
    font = font_manager.load_font(family, min_size, weight, italic)
    if allow_wrap:
        sample_bbox = draw.textbbox((0, 0), "W", font=font)
        avg_char_w = max(1, sample_bbox[2] - sample_bbox[0])
        chars_per_line = max(1, int(box_width / avg_char_w))
        wrapped = textwrap.wrap(text, width=chars_per_line, break_long_words=True)[:max_lines]
        if not wrapped:
            wrapped = [text]
    else:
        wrapped = [text]

    tw, th = _measure_lines(wrapped, font, draw, line_height)

    return SmartFitResult(
        lines=wrapped,
        font=font,
        font_size=min_size,
        text_width=tw,
        text_height=th,
        overflowed=True,
        overflow_detail={
            "element_id": element_id,
            "field": field_name,
            "required_width": tw,
            "available_width": box_width,
            "required_height": th,
            "available_height": box_height,
            "minimum_font_size": min_size,
        },
    )
