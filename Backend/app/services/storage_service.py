import os
import uuid
import io
import mimetypes
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from PIL import Image
from app.core.config import settings
from app.core.exceptions import ValidationError


class StorageService:
    @classmethod
    def get_base_dir(cls) -> Path:
        base = Path(settings.STORAGE_DIR)
        base.mkdir(parents=True, exist_ok=True)
        return base

    @classmethod
    def validate_file(cls, filename: str, content: bytes, content_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate file size, extension, MIME type, and image signatures.
        Returns dict with validated metadata: width, height, mime_type, size.
        """
        size_bytes = len(content)
        max_bytes = settings.MAX_ASSET_SIZE_MB * 1024 * 1024
        if size_bytes > max_bytes:
            raise ValidationError(
                message=f"File exceeds maximum allowed size of {settings.MAX_ASSET_SIZE_MB}MB",
                code="FILE_TOO_LARGE"
            )

        if size_bytes == 0:
            raise ValidationError(message="Uploaded file is empty", code="EMPTY_FILE")

        # Determine/normalize mime type
        mime = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"

        # SVG validation
        if filename.lower().endswith(".svg") or mime == "image/svg+xml":
            # Basic SVG content check
            try:
                head = content[:1024].decode("utf-8", errors="ignore").lower()
                if "<svg" not in head and "<?xml" not in head:
                    raise ValidationError(message="Invalid SVG file content", code="INVALID_SVG")
                return {
                    "mime_type": "image/svg+xml",
                    "size": size_bytes,
                    "width": 1920,
                    "height": 1080
                }
            except Exception as e:
                raise ValidationError(message=f"Corrupted or invalid SVG: {str(e)}", code="INVALID_SVG")

        # Raster image validation (PNG, JPEG) via Pillow
        try:
            with Image.open(io.BytesIO(content)) as img:
                img_format = img.format  # 'PNG', 'JPEG'
                if img_format not in ["PNG", "JPEG"]:
                    raise ValidationError(
                        message=f"Unsupported image format: {img_format}. Allowed: PNG, JPEG, SVG.",
                        code="UNSUPPORTED_FORMAT"
                    )

                mime_type = "image/png" if img_format == "PNG" else "image/jpeg"
                width, height = img.size

                if width < 100 or height < 100:
                    raise ValidationError(
                        message="Image dimensions too small. Minimum dimension is 100x100px.",
                        code="IMAGE_TOO_SMALL"
                    )

                if width > 10000 or height > 10000:
                    raise ValidationError(
                        message="Image dimensions exceed maximum allowed limit of 10000x10000px.",
                        code="IMAGE_TOO_LARGE"
                    )

                return {
                    "mime_type": mime_type,
                    "size": size_bytes,
                    "width": width,
                    "height": height
                }
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(
                message=f"Invalid or corrupted image file: {str(e)}",
                code="INVALID_IMAGE_FILE"
            )

    @classmethod
    def save_file(
        cls,
        content: bytes,
        filename: str,
        org_id: str,
        template_id: Optional[str] = None
    ) -> Tuple[str, Path]:
        """
        Save file to isolated storage directory:
        storage/assets/{org_id}/{template_id}/{uuid}_{clean_filename}
        Returns: (storage_key, file_path)
        """
        # Clean filename
        clean_name = os.path.basename(filename).replace(" ", "_")
        unique_prefix = uuid.uuid4().hex[:12]
        stored_filename = f"{unique_prefix}_{clean_name}"

        # Target directory structure
        tmpl_subpath = template_id if template_id else "common"
        rel_dir = Path("assets") / org_id / tmpl_subpath
        target_dir = cls.get_base_dir() / rel_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / stored_filename
        with open(target_path, "wb") as f:
            f.write(content)

        # Storage key is relative path using forward slashes
        storage_key = str((rel_dir / stored_filename).as_posix())
        return storage_key, target_path

    @classmethod
    def get_file_path(cls, storage_key: str) -> Path:
        return cls.get_base_dir() / storage_key

    @classmethod
    def read_file(cls, storage_key: str) -> Optional[bytes]:
        path = cls.get_file_path(storage_key)
        if not path.is_file():
            return None
        with open(path, "rb") as f:
            return f.read()

    @classmethod
    def delete_file(cls, storage_key: str) -> bool:
        path = cls.get_file_path(storage_key)
        if path.is_file():
            try:
                path.unlink()
                return True
            except OSError:
                return False
        return False
