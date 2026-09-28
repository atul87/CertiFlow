"""
QRRenderer — P3.33–P3.35

Generates a QR code from a URL and composites it onto the canvas.
Uses qrcode[pil] which is already in requirements.txt.
Error-correction level: H (30 %) by default — survives logo overlays.
"""
from __future__ import annotations
import logging
import qrcode
from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_M, ERROR_CORRECT_L
from PIL import Image

logger = logging.getLogger(__name__)

_EC_MAP = {
    "H": ERROR_CORRECT_H,
    "M": ERROR_CORRECT_M,
    "L": ERROR_CORRECT_L,
}


def generate_qr_image(
    content: str,
    size: int = 300,
    error_correction: str = "H",
    fill_color: str = "black",
    back_color: str = "white",
) -> Image.Image:
    """
    Return a square PIL RGBA image of the QR code.
    :param content:          QR data — typically a verification URL
    :param size:             Target pixel size (square)
    :param error_correction: 'H', 'M', or 'L'
    :param fill_color:       Module (dark square) colour
    :param back_color:       Background colour
    """
    ec = _EC_MAP.get(error_correction.upper(), ERROR_CORRECT_H)
    qr = qrcode.QRCode(
        error_correction=ec,
        box_size=10,
        border=2,
    )
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img


def render_qr_element(
    canvas: Image.Image,
    element: dict,
    content: str,
) -> None:
    """
    Composite a QR code onto the canvas at the element's position/size.

    :param canvas:  RGBA PIL image (mutated in-place)
    :param element: dict with position, size, style (error_correction, opacity)
    :param content: The URL / data string to encode in the QR
    """
    if not content:
        logger.warning("QRRenderer: empty content, skipping QR render")
        return

    pos = element.get("position", {})
    size_dict = element.get("size", {})
    style = element.get("style", {})

    x = int(pos.get("x", 0))
    y = int(pos.get("y", 0))
    w = max(20, int(size_dict.get("width", 300)))
    h = max(20, int(size_dict.get("height", 300)))
    ec = style.get("error_correction", "H")
    opacity = float(style.get("opacity", 1.0))

    try:
        qr_img = generate_qr_image(content, size=min(w, h), error_correction=ec)
    except Exception as exc:
        logger.error("QRRenderer: failed to generate QR — %s", exc)
        return

    if opacity < 1.0:
        r, g, b, a = qr_img.split()
        a = a.point(lambda v: int(v * opacity))
        qr_img = Image.merge("RGBA", (r, g, b, a))

    # Center within element bounding box
    paste_x = x + (w - qr_img.width) // 2
    paste_y = y + (h - qr_img.height) // 2
    canvas.alpha_composite(qr_img, dest=(paste_x, paste_y))
