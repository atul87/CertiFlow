"""
ImageRenderer — P3.24–P3.28

Composites a PIL image (logo, signature, seal, background, etc.) onto the
certificate canvas.  Supports contain / cover / stretch fit modes and opacity.
"""
from __future__ import annotations
import io
import logging
from PIL import Image

logger = logging.getLogger(__name__)


def _fit_contain(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Scale img so it fits inside (target_w, target_h) preserving aspect ratio."""
    img_w, img_h = img.size
    scale = min(target_w / img_w, target_h / img_h)
    new_w = max(1, int(img_w * scale))
    new_h = max(1, int(img_h * scale))
    return img.resize((new_w, new_h), Image.Resampling.LANCZOS)


def _fit_cover(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Scale img so it covers (target_w, target_h) then center-crop."""
    img_w, img_h = img.size
    scale = max(target_w / img_w, target_h / img_h)
    new_w = max(1, int(img_w * scale))
    new_h = max(1, int(img_h * scale))
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def _apply_opacity(img: Image.Image, opacity: float) -> Image.Image:
    """Return a copy of img with alpha multiplied by opacity (0.0–1.0)."""
    if opacity >= 1.0:
        return img
    img = img.convert("RGBA")
    r, g, b, a = img.split()
    a = a.point(lambda v: int(v * opacity))
    return Image.merge("RGBA", (r, g, b, a))


def render_image_element(
    canvas: Image.Image,
    element: dict,
    image_bytes: bytes,
) -> None:
    """
    Composite image_bytes onto canvas according to element's position/size/style.

    :param canvas:       RGBA PIL image (mutated in-place)
    :param element:      dict with position, size, style (fit_mode, opacity, rotation)
    :param image_bytes:  raw PNG/JPEG bytes
    """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    except Exception as exc:
        logger.warning("ImageRenderer: could not open image — %s", exc)
        return

    pos = element.get("position", {})
    size = element.get("size", {})
    style = element.get("style", {})

    x = int(pos.get("x", 0))
    y = int(pos.get("y", 0))
    w = max(1, int(size.get("width", 100)))
    h = max(1, int(size.get("height", 100)))
    fit_mode = style.get("fit_mode", "contain")
    opacity = float(style.get("opacity", 1.0))
    rotation = float(element.get("rotation", 0))

    # 1. Fit
    if fit_mode == "cover":
        img = _fit_cover(img, w, h)
    elif fit_mode == "stretch":
        img = img.resize((w, h), Image.Resampling.LANCZOS)
    else:  # contain (default — preserves aspect ratio)
        img = _fit_contain(img, w, h)

    # 2. Opacity
    if opacity < 1.0:
        img = _apply_opacity(img, opacity)

    # 3. Rotation
    if rotation != 0:
        img = img.rotate(-rotation, expand=True, resample=Image.Resampling.BICUBIC)

    # 4. Center within the element bounding box
    paste_x = x + (w - img.width) // 2
    paste_y = y + (h - img.height) // 2

    canvas.alpha_composite(img, dest=(paste_x, paste_y))
