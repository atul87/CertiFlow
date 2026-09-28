"""
ShapeRenderer — P3.29–P3.32

Draws geometric shapes (rectangle, rounded_rectangle, circle, line) onto
a PIL RGBA canvas with fill, stroke, opacity, and rotation support.
"""
from __future__ import annotations
import logging
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)


def _parse_color(val: str | None, opacity: float = 1.0):
    if not val or val.lower() == "none":
        return None
    h = val.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    a = int(min(max(opacity, 0.0), 1.0) * 255)
    return (r, g, b, a)


def render_shape_element(
    canvas: Image.Image,
    element: dict,
) -> None:
    """
    Draw a shape element onto the canvas.

    Supported types: rectangle, rounded_rectangle, circle (ellipse), line.
    """
    pos = element.get("position", {})
    size = element.get("size", {})
    style = element.get("style", {})
    shape_type = element.get("shape_type", element.get("type", "rectangle"))

    x = int(pos.get("x", 0))
    y = int(pos.get("y", 0))
    w = max(1, int(size.get("width", 100)))
    h = max(1, int(size.get("height", 100)))
    opacity = float(style.get("opacity", 1.0))
    rotation = float(element.get("rotation", 0))
    stroke_width = int(style.get("stroke_width", 0))
    radius = int(style.get("radius", 10))  # for rounded_rectangle

    fill = _parse_color(style.get("fill"), opacity)
    stroke = _parse_color(style.get("stroke"), opacity)

    # Draw on a transparent layer then composite
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    bbox = [0, 0, w - 1, h - 1]

    if shape_type in ("rectangle", "rect"):
        draw.rectangle(bbox, fill=fill, outline=stroke, width=stroke_width or 1)

    elif shape_type == "rounded_rectangle":
        draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=stroke, width=stroke_width or 1)

    elif shape_type in ("circle", "ellipse"):
        draw.ellipse(bbox, fill=fill, outline=stroke, width=stroke_width or 1)

    elif shape_type == "line":
        # Draw a horizontal line scaled to width
        mid_y = h // 2
        lw = stroke_width or 2
        draw.line([(0, mid_y), (w, mid_y)], fill=stroke or fill, width=lw)

    else:
        logger.warning("ShapeRenderer: unknown shape_type '%s', skipping", shape_type)
        return

    if rotation != 0:
        layer = layer.rotate(-rotation, expand=True, resample=Image.Resampling.BICUBIC)

    canvas.alpha_composite(layer, dest=(x, y))
