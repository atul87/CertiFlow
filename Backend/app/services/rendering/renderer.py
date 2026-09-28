"""
CertificateRenderer — P3.37

Orchestrates the full render pipeline for a single certificate:
  1. Create blank RGBA canvas at template dimensions
  2. Draw background asset (if any)
  3. Sort elements by z_index (P3.30)
  4. For each element dispatch to the appropriate sub-renderer
  5. Return high-res canvas + PNG preview bytes

Returns:
  {
    "canvas": PIL.Image,       # full-resolution RGBA
    "preview_bytes": bytes,    # 1600-px-wide PNG
    "overflows": [...],        # SmartFit overflow warnings
    "diagnostics": {...},      # timing + counts
  }
"""
from __future__ import annotations
import io
import logging
import time
from typing import Any, Optional

from PIL import Image, ImageDraw

from app.services.rendering.text_renderer import render_text_element
from app.services.rendering.image_renderer import render_image_element
from app.services.rendering.shape_renderer import render_shape_element
from app.services.rendering.qr_renderer import render_qr_element

logger = logging.getLogger(__name__)

_SHAPE_TYPES = {"rectangle", "rect", "rounded_rectangle", "circle", "ellipse", "line", "shape"}
_PREVIEW_MAX_WIDTH = 1600


def _build_background(canvas_w: int, canvas_h: int, bg_image_bytes: Optional[bytes]) -> Image.Image:
    """Create the initial RGBA canvas with optional background image."""
    if bg_image_bytes:
        try:
            raw = Image.open(io.BytesIO(bg_image_bytes)).convert("RGBA")
            return raw.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
        except Exception as exc:
            logger.warning("Renderer: could not open background — %s", exc)

    # Default parchment-style background
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (252, 252, 250, 255))
    draw = ImageDraw.Draw(canvas)
    margin = int(canvas_w * 0.025)
    border_w = max(2, int(canvas_w * 0.003))
    draw.rectangle(
        [margin, margin, canvas_w - margin, canvas_h - margin],
        outline=(212, 175, 55, 255),
        width=border_w,
    )
    # Inner double border
    margin2 = margin + border_w * 3
    draw.rectangle(
        [margin2, margin2, canvas_w - margin2, canvas_h - margin2],
        outline=(212, 175, 55, 180),
        width=max(1, border_w // 2),
    )
    return canvas


def _make_preview(canvas: Image.Image, max_width: int = _PREVIEW_MAX_WIDTH) -> bytes:
    """Return downscaled PNG bytes for web preview."""
    w, h = canvas.size
    if w > max_width:
        scale = max_width / w
        canvas = canvas.resize((max_width, int(h * scale)), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    canvas.convert("RGB").save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def render_certificate(
    version_doc: dict[str, Any],
    resolved_data: dict[str, Any],
    asset_loader: Any,  # callable: asset_id -> Optional[bytes]
    bg_image_bytes: Optional[bytes] = None,
    max_preview_width: int = _PREVIEW_MAX_WIDTH,
) -> dict[str, Any]:
    """
    Full render pass.

    :param version_doc:    Template version dict with elements, width, height
    :param resolved_data:  Fully resolved placeholder data (all {{keys}} already substituted)
    :param asset_loader:   Sync callable: asset_id (str) -> Optional[bytes]
    :param bg_image_bytes: Pre-loaded background image bytes (optional)
    :param max_preview_width: PNG preview downsample width
    :returns: dict with canvas, preview_bytes, overflows, diagnostics
    """
    t_start = time.monotonic()

    canvas_w = int(version_doc.get("width", 3508))
    canvas_h = int(version_doc.get("height", 2480))

    # 1. Background
    canvas = _build_background(canvas_w, canvas_h, bg_image_bytes)

    # 2. Sort elements by z_index  (P3.30)
    elements = list(version_doc.get("elements", []))
    elements.sort(key=lambda e: int(e.get("z_index", e.get("zIndex", 0))))

    overflows: list = []
    text_count = 0
    image_count = 0
    shape_count = 0
    qr_count = 0

    # 3. Render each element
    for elem in elements:
        elem_type = elem.get("type", "text")

        # --- TEXT ---
        if elem_type == "text":
            content_template = elem.get("content", "")
            # content is already resolved before calling this function
            # resolved_data has final values; substitute remaining
            from app.services.placeholder_service import PlaceholderService
            resolved_text = PlaceholderService.substitute_text(
                content_template, resolved_data, use_sample_fallback=False
            )
            render_text_element(canvas, elem, resolved_text, overflows)
            text_count += 1

        # --- QR ---
        elif elem_type == "qr":
            qr_content_template = elem.get("content", "{{verification_url}}")
            from app.services.placeholder_service import PlaceholderService
            qr_content = PlaceholderService.substitute_text(
                qr_content_template, resolved_data, use_sample_fallback=False
            )
            render_qr_element(canvas, elem, qr_content)
            qr_count += 1

        # --- IMAGE ---
        elif elem_type == "image":
            asset_id = elem.get("asset_id")
            if asset_id:
                img_bytes = asset_loader(asset_id)
                if img_bytes:
                    render_image_element(canvas, elem, img_bytes)
            image_count += 1

        # --- SHAPE / LINE ---
        elif elem_type in _SHAPE_TYPES:
            render_shape_element(canvas, elem)
            shape_count += 1

        else:
            logger.debug("Renderer: skipping unknown element type '%s'", elem_type)

    t_render = time.monotonic()

    # 4. Build preview
    preview_bytes = _make_preview(canvas, max_preview_width)

    diagnostics = {
        "canvas_width": canvas_w,
        "canvas_height": canvas_h,
        "element_count": len(elements),
        "text_element_count": text_count,
        "image_element_count": image_count,
        "shape_element_count": shape_count,
        "qr_element_count": qr_count,
        "overflow_count": len(overflows),
        "render_time_ms": round((t_render - t_start) * 1000, 1),
    }

    return {
        "canvas": canvas,
        "preview_bytes": preview_bytes,
        "overflows": overflows,
        "diagnostics": diagnostics,
    }
