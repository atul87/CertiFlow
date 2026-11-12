import os
import uuid
import io
import mimetypes
from pathlib import Path, PurePosixPath
from functools import lru_cache
from typing import Tuple, Optional, Dict, Any
from PIL import Image
from app.core.config import settings
from app.core.exceptions import ValidationError


@lru_cache(maxsize=1)
def _s3_client():
    """Create one S3-compatible client per process, only when object storage is enabled."""
    import boto3
    from botocore.config import Config

    kwargs = {
        "region_name": settings.S3_REGION or "auto",
        "aws_access_key_id": settings.S3_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.S3_SECRET_ACCESS_KEY,
        "config": Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    }
    if settings.S3_ENDPOINT:
        kwargs["endpoint_url"] = settings.S3_ENDPOINT
    return boto3.client("s3", **kwargs)


class StorageService:
    @classmethod
    def _uses_s3(cls) -> bool:
        return settings.STORAGE_TYPE.lower() == "s3"

    @classmethod
    def _safe_key(cls, storage_key: str) -> str:
        key = str(storage_key).replace(chr(92), "/").lstrip("/")
        path = PurePosixPath(key)
        if not key or any(part in ("", ".", "..") for part in path.parts):
            raise ValueError("Invalid storage key")
        return path.as_posix()

    @classmethod
    def get_base_dir(cls) -> Path:
        """Return the local storage root. Object-storage callers must use key-based APIs."""
        if cls._uses_s3():
            raise RuntimeError("Local filesystem paths are unavailable when STORAGE_TYPE=s3; use StorageService key APIs.")
        base = Path(settings.STORAGE_DIR)
        base.mkdir(parents=True, exist_ok=True)
        return base

    @classmethod
    def save_bytes(cls, content: bytes, storage_key: str, content_type: Optional[str] = None) -> str:
        key = cls._safe_key(storage_key)
        if cls._uses_s3():
            _s3_client().put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=key,
                Body=content,
                ContentType=content_type or "application/octet-stream",
            )
        else:
            target = cls.get_base_dir() / Path(*PurePosixPath(key).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        return key

    @classmethod
    def validate_file(cls, filename: str, content: bytes, content_type: Optional[str] = None) -> Dict[str, Any]:
        """Validate file size, extension, MIME type, and image signatures."""
        size_bytes = len(content)
        max_bytes = settings.MAX_ASSET_SIZE_MB * 1024 * 1024
        if size_bytes > max_bytes:
            raise ValidationError(
                message=f"File exceeds maximum allowed size of {settings.MAX_ASSET_SIZE_MB}MB",
                code="FILE_TOO_LARGE"
            )
        if size_bytes == 0:
            raise ValidationError(message="Uploaded file is empty", code="EMPTY_FILE")

        mime = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        from app.security.file_security import FileSecurity

        if filename.lower().endswith(".svg") or mime == "image/svg+xml":
            try:
                head = content[:1024].decode("utf-8", errors="ignore").lower()
                if "<svg" not in head and "<?xml" not in head:
                    raise ValidationError(message="Invalid SVG file content", code="INVALID_SVG")
                sanitized_svg = FileSecurity.sanitize_svg(content)
                return {"mime_type": "image/svg+xml", "size": len(sanitized_svg),
                        "width": 1920, "height": 1080, "sanitized_content": sanitized_svg}
            except Exception as e:
                if isinstance(e, ValidationError):
                    raise
                raise ValidationError(message=f"Corrupted or invalid SVG: {str(e)}", code="INVALID_SVG")

        if filename.lower().endswith(".png") and not FileSecurity.validate_magic_bytes(content, "png"):
            raise ValidationError(message="File magic bytes do not match expected PNG signature", code="INVALID_IMAGE_FILE")
        if filename.lower().endswith((".jpg", ".jpeg")) and not FileSecurity.validate_magic_bytes(content, "jpeg"):
            raise ValidationError(message="File magic bytes do not match expected JPEG signature", code="INVALID_IMAGE_FILE")

        try:
            with Image.open(io.BytesIO(content)) as img:
                img_format = img.format
                if img_format not in ["PNG", "JPEG"]:
                    raise ValidationError(message=f"Unsupported image format: {img_format}. Allowed: PNG, JPEG, SVG.", code="UNSUPPORTED_FORMAT")
                width, height = img.size
                if width < 100 or height < 100:
                    raise ValidationError(message="Image dimensions too small. Minimum dimension is 100x100px.", code="IMAGE_TOO_SMALL")
                if width > 10000 or height > 10000:
                    raise ValidationError(message="Image dimensions exceed maximum allowed limit of 10000x10000px.", code="IMAGE_TOO_LARGE")
                return {"mime_type": "image/png" if img_format == "PNG" else "image/jpeg",
                        "size": size_bytes, "width": width, "height": height}
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(message=f"Invalid or corrupted image file: {str(e)}", code="INVALID_IMAGE_FILE")

    @classmethod
    def save_file(cls, content: bytes, filename: str, org_id: str,
                  template_id: Optional[str] = None) -> Tuple[str, Path]:
        clean_name = os.path.basename(filename).replace(" ", "_")
        stored_filename = f"{uuid.uuid4().hex[:12]}_{clean_name}"
        tmpl_subpath = template_id if template_id else "common"
        rel_key = (Path("assets") / org_id / tmpl_subpath / stored_filename).as_posix()
        mime = mimetypes.guess_type(clean_name)[0] or "application/octet-stream"
        key = cls.save_bytes(content, rel_key, mime)
        # The second value is retained for backwards compatibility; callers should persist the key.
        return key, (Path(settings.STORAGE_DIR) / key if not cls._uses_s3() else Path(key))

    @classmethod
    def get_file_path(cls, storage_key: str) -> Path:
        if cls._uses_s3():
            raise RuntimeError("Object-storage objects do not have local filesystem paths.")
        return cls.get_base_dir() / Path(*PurePosixPath(cls._safe_key(storage_key)).parts)

    @classmethod
    def read_file(cls, storage_key: str) -> Optional[bytes]:
        key = cls._safe_key(storage_key)
        if cls._uses_s3():
            try:
                response = _s3_client().get_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
                return response["Body"].read()
            except Exception as exc:
                from botocore.exceptions import ClientError
                if isinstance(exc, ClientError) and exc.response.get("Error", {}).get("Code") in ("NoSuchKey", "404", "NotFound"):
                    return None
                raise
        path = cls.get_file_path(key)
        return path.read_bytes() if path.is_file() else None

    @classmethod
    async def download_file(cls, storage_key: str) -> bytes:
        data = cls.read_file(storage_key)
        if data is None:
            raise FileNotFoundError(f"Storage key {storage_key} not found")
        return data

    @classmethod
    def get_prefix_size(cls, prefix: str) -> int:
        """Return total stored bytes under a logical prefix for usage reporting."""
        clean_prefix = cls._safe_key(prefix).rstrip("/") + "/"
        if cls._uses_s3():
            total = 0
            paginator = _s3_client().get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=settings.S3_BUCKET_NAME, Prefix=clean_prefix):
                total += sum(item.get("Size", 0) for item in page.get("Contents", []))
            return total
        directory = cls.get_base_dir() / Path(*PurePosixPath(clean_prefix.rstrip("/")).parts)
        if not directory.is_dir():
            return 0
        return sum(path.stat().st_size for path in directory.rglob("*") if path.is_file())

    @classmethod
    def delete_file(cls, storage_key: str) -> bool:
        key = cls._safe_key(storage_key)
        if cls._uses_s3():
            _s3_client().delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
            return True
        path = cls.get_file_path(key)
        if path.is_file():
            try:
                path.unlink()
                return True
            except OSError:
                return False
        return False
