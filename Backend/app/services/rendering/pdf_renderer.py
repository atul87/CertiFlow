"""
PDFRenderer — P3.36–P3.42

Converts a high-resolution PIL Image into a single-page PDF document.
Uses ReportLab (PDF/point dimensions) to preserve:
  - Exact canvas dimensions (A4 landscape ≈ 3508×2480 px @ 300 DPI)
  - PDF metadata (Title, Author, Subject, Creator)
  - SHA-256 hash of the final PDF bytes

ReportLab is used in PIL-image-to-canvas mode:
  canvas image → PNG bytes → embedded into PDF page at correct size
"""
from __future__ import annotations
import hashlib
import io
import logging
from PIL import Image

logger = logging.getLogger(__name__)

# Points per pixel at 300 DPI  (1 inch = 72 pt; 1 px @300dpi = 72/300 pt)
_PT_PER_PX_300DPI = 72.0 / 300.0


def render_pdf(
    canvas_image: Image.Image,
    dpi: int = 300,
    title: str = "Certificate",
    author: str = "CertiFlow",
    subject: str = "Certificate of Completion",
    creator: str = "CertiFlow Certificate Platform",
) -> bytes:
    """
    Convert canvas_image → single-page PDF bytes with embedded metadata.

    :param canvas_image: Final high-res PIL RGBA/RGB image
    :param dpi:          DPI used for page size calculation (default 300)
    :param title:        PDF /Title metadata
    :param author:       PDF /Author metadata
    :param subject:      PDF /Subject metadata
    :param creator:      PDF /Creator metadata
    :returns:            Raw PDF file bytes
    """
    try:
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.utils import ImageReader
    except ImportError as exc:
        raise RuntimeError(
            "reportlab is required for PDF generation. "
            "Install it via: pip install reportlab>=4.0.0"
        ) from exc

    img_rgb = canvas_image.convert("RGB")
    img_w_px, img_h_px = img_rgb.size

    # Convert pixel dimensions to PDF points
    pt_per_px = 72.0 / dpi
    page_w_pt = img_w_px * pt_per_px
    page_h_pt = img_h_px * pt_per_px

    # Encode image as PNG bytes for embedding
    img_buf = io.BytesIO()
    img_rgb.save(img_buf, format="PNG", optimize=False)
    img_buf.seek(0)

    # Write PDF
    pdf_buf = io.BytesIO()
    c = rl_canvas.Canvas(pdf_buf, pagesize=(page_w_pt, page_h_pt))

    # Metadata — P3.40
    c.setTitle(title)
    c.setAuthor(author)
    c.setSubject(subject)
    c.setCreator(creator)

    # Draw full-page image (ReportLab origin is bottom-left)
    img_reader = ImageReader(img_buf)
    c.drawImage(img_reader, 0, 0, width=page_w_pt, height=page_h_pt)

    c.showPage()
    c.save()

    return pdf_buf.getvalue()


def sha256_of_bytes(data: bytes) -> str:
    """Return lowercase hex SHA-256 of data bytes — P3.41 / P3.42."""
    return hashlib.sha256(data).hexdigest()
