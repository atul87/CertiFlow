"""
TextRenderer — P3.11, P3.17–P3.23

Renders a resolved text string onto a PIL RGBA canvas element with:
  - SmartFit (shrink + wrap)
  - Horizontal alignment: left / center / right / justify
  - Vertical alignment: top / middle / bottom
  - Opacity
  - Rotation (PIL rotate on a temporary layer)
"""
from __future__ import annotations
import logging
from typing import Optional, List
from PIL import Image, ImageDraw, ImageFont
from app.services.rendering.smart_fit import smart_fit, SmartFitResult

logger = logging.getLogger(__name__)


def _hex_to_rgba(hex_color: str, opacity: float = 1.0):
    """Convert #RRGGBB / #RGB to RGBA tuple with opacity."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    a = int(min(max(opacity, 0.0), 1.0) * 255)
    return (r, g, b, a)


def render_text_element(
    canvas: Image.Image,
    element: dict,
    resolved_text: str,
    overflows: list,
) -> None:
    """
    Draws the resolved_text onto the canvas in-place.

    :param canvas: RGBA PIL image (mutated in-place)
    :param element: dict with keys: id, position, size, style
    :param resolved_text: already-substituted text string
    :param overflows: mutable list — SmartFit overflow dicts are appended here
    """
    if not resolved_text:
        return

    pos = element.get("position", {})
    size = element.get("size", {})
    style = element.get("style", {})

    x = int(pos.get("x", 0))
    y = int(pos.get("y", 0))
    w = max(1, int(size.get("width", 200)))
    h = max(1, int(size.get("height", 60)))

    family = style.get("font_family", "Inter")
    font_size = int(style.get("font_size", 48))
    weight = int(style.get("font_weight", 400))
    italic = bool(style.get("italic", False))
    color_hex = style.get("color", "#000000")
    alignment = style.get("alignment", "center")
    v_alignment = style.get("vertical_alignment", "middle")
    opacity = float(style.get("opacity", 1.0))
    line_height = float(style.get("line_height", 1.2))
    min_size = int(style.get("min_font_size", 14))
    max_lines = int(style.get("max_lines", 20))
    rotation = float(element.get("rotation", 0))

    result: SmartFitResult = smart_fit(
        text=resolved_text,
        box_width=w,
        box_height=h,
        family=family,
        initial_size=font_size,
        min_size=min_size,
        weight=weight,
        italic=italic,
        line_height=line_height,
        max_lines=max_lines,
        allow_wrap=True,
        allow_shrink=True,
        element_id=element.get("id", ""),
        field_name=element.get("content", ""),
    )

    if result.overflowed and result.overflow_detail:
        overflows.append(result.overflow_detail)

    font = result.font
    lines = result.lines
    color = _hex_to_rgba(color_hex, opacity)

    # Measure each line for alignment
    dummy = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy)

    line_metrics: List[dict] = []
    for line in lines:
        bbox = dummy_draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        line_metrics.append({"text": line, "w": lw, "h": lh})

    total_h = int(sum(m["h"] * line_height for m in line_metrics))

    # Vertical start offset
    if v_alignment == "bottom":
        start_y = y + h - total_h
    elif v_alignment == "middle":
        start_y = y + (h - total_h) // 2
    else:  # top
        start_y = y

    # Create a transparent layer the size of the element, render text, then composite
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer_draw = ImageDraw.Draw(layer)

    cur_y = start_y - y  # relative to layer
    for m in line_metrics:
        if alignment == "center":
            draw_x = (w - m["w"]) // 2
        elif alignment == "right":
            draw_x = w - m["w"]
        else:  # left / justify (simple left for now)
            draw_x = 0

        layer_draw.text((draw_x, cur_y), m["text"], font=font, fill=color)
        cur_y += int(m["h"] * line_height)

    # Handle rotation
    if rotation != 0:
        layer = layer.rotate(-rotation, expand=True, resample=Image.Resampling.BICUBIC)

    canvas.alpha_composite(layer, dest=(x, y))
