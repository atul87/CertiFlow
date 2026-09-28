import io
import base64
import logging
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont
import qrcode
from app.services.storage_service import StorageService
from app.services.placeholder_service import PlaceholderService
from app.repositories.asset_repository import AssetRepository

logger = logging.getLogger(__name__)


class PreviewService:
    @classmethod
    async def render_preview_base64(
        cls,
        version_doc: Dict[str, Any],
        sample_data: Optional[Dict[str, Any]] = None,
        max_preview_width: int = 1600
    ) -> str:
        """
        Generate lightweight rendered PNG preview of certificate design with placeholders substituted.
        Returns base64 data URL: 'data:image/png;base64,...'
        """
        sample_dict = sample_data or {}
        canvas_width = int(version_doc.get("width", 3508))
        canvas_height = int(version_doc.get("height", 2480))

        # 1. Initialize canvas from background asset or clean canvas
        bg_asset_id = version_doc.get("background_asset_id")
        canvas_img = None

        if bg_asset_id:
            asset = await AssetRepository.get_by_id(str(bg_asset_id))
            if asset and asset.get("storage_key"):
                bg_bytes = StorageService.read_file(asset["storage_key"])
                if bg_bytes:
                    try:
                        raw_bg = Image.open(io.BytesIO(bg_bytes)).convert("RGBA")
                        canvas_img = raw_bg.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                    except Exception as e:
                        logger.warning("Could not open background image: %s", e)

        if canvas_img is None:
            # Create default parchment-style certificate background
            canvas_img = Image.new("RGBA", (canvas_width, canvas_height), (252, 252, 250, 255))
            # Draw subtle gold border
            draw = ImageDraw.Draw(canvas_img)
            border_margin = int(canvas_width * 0.03)
            draw.rectangle(
                [border_margin, border_margin, canvas_width - border_margin, canvas_height - border_margin],
                outline=(212, 175, 55, 255),
                width=int(canvas_width * 0.004)
            )

        draw = ImageDraw.Draw(canvas_img)

        # 2. Render elements in order
        elements = version_doc.get("elements", [])
        for elem in elements:
            elem_type = elem.get("type", "text")
            pos = elem.get("position", {})
            size = elem.get("size", {})
            style = elem.get("style", {})

            x = int(pos.get("x", 0))
            y = int(pos.get("y", 0))
            w = int(size.get("width", 100))
            h = int(size.get("height", 50))

            if elem_type == "text":
                content = elem.get("content", "")
                rendered_text = PlaceholderService.substitute_text(content, sample_dict, use_sample_fallback=True)

                font_size = int(style.get("font_size", 48))
                color_hex = style.get("color", "#000000")
                alignment = style.get("alignment", "center")

                # Try loading font or fallback to default
                try:
                    font = ImageFont.load_default(size=font_size)
                except Exception:
                    font = ImageFont.load_default()

                # Calculate text dimensions for alignment
                bbox = draw.textbbox((0, 0), rendered_text, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]

                draw_x = x
                if alignment == "center":
                    draw_x = x + (w - text_w) // 2
                elif alignment == "right":
                    draw_x = x + w - text_w

                draw.text((draw_x, y), rendered_text, fill=color_hex, font=font)

            elif elem_type == "qr":
                # Generate QR code preview
                raw_content = elem.get("content", "{{verification_url}}")
                qr_content = PlaceholderService.substitute_text(raw_content, sample_dict, use_sample_fallback=True)
                qr = qrcode.QRCode(box_size=10, border=1)
                qr.add_data(qr_content)
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
                qr_resized = qr_img.resize((w, h), Image.Resampling.LANCZOS)
                canvas_img.paste(qr_resized, (x, y), qr_resized)

            elif elem_type == "image":
                asset_id = elem.get("asset_id")
                if asset_id:
                    asset = await AssetRepository.get_by_id(str(asset_id))
                    if asset and asset.get("storage_key"):
                        img_bytes = StorageService.read_file(asset["storage_key"])
                        if img_bytes:
                            try:
                                el_img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
                                el_resized = el_img.resize((w, h), Image.Resampling.LANCZOS)
                                canvas_img.paste(el_resized, (x, y), el_resized)
                            except Exception:
                                pass

        # 3. Scale down for fast web preview
        if canvas_width > max_preview_width:
            aspect = canvas_height / canvas_width
            preview_w = max_preview_width
            preview_h = int(preview_w * aspect)
            preview_img = canvas_img.resize((preview_w, preview_h), Image.Resampling.LANCZOS)
        else:
            preview_img = canvas_img

        # 4. Convert to base64 PNG data URL
        buf = io.BytesIO()
        preview_img.convert("RGB").save(buf, format="PNG", quality=90, optimize=True)
        b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b64_str}"
