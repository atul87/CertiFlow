"""
File Upload Security & Content Sanitization (P9).
Guards against malicious file uploads, executable masquerading, SVG XSS/XXE,
and ZIP bombs/Zip Slip path traversal vulnerabilities.
"""
from __future__ import annotations
import io
import re
import zipfile
from typing import Dict, Any, Optional, List, Tuple
from app.core.config import settings
from app.core.exceptions import ValidationError

# Magic byte signatures
MAGIC_BYTES = {
    "png": b"\x89PNG\r\n\x1a\n",
    "jpeg": b"\xff\xd8\xff",
    "pdf": b"%PDF-",
    "zip": b"PK\x03\x04",
    "ttf": b"\x00\x01\x00\x00",
    "otf": b"OTTO",
    "woff": b"wOFF",
    "woff2": b"wOF2",
}


class FileSecurity:
    @classmethod
    def validate_magic_bytes(cls, content: bytes, expected_type: str) -> bool:
        """
        Verify that file content header matches standard magic bytes for expected format.
        """
        if not content:
            return False

        exp = expected_type.lower().strip()
        if exp in ("png", "image/png"):
            return content.startswith(MAGIC_BYTES["png"])

        if exp in ("jpeg", "jpg", "image/jpeg", "image/jpg"):
            return content.startswith(MAGIC_BYTES["jpeg"])

        if exp in ("pdf", "application/pdf"):
            return content.startswith(MAGIC_BYTES["pdf"])

        if exp in ("xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"):
            # XLSX files are standard ZIP containers
            return content.startswith(MAGIC_BYTES["zip"])

        if exp in ("zip", "application/zip"):
            return content.startswith(MAGIC_BYTES["zip"])

        if exp in ("ttf", "font/ttf"):
            return content.startswith(MAGIC_BYTES["ttf"])

        if exp in ("otf", "font/otf"):
            return content.startswith(MAGIC_BYTES["otf"])

        if exp in ("woff", "font/woff"):
            return content.startswith(MAGIC_BYTES["woff"])

        if exp in ("woff2", "font/woff2"):
            return content.startswith(MAGIC_BYTES["woff2"])

        if exp in ("csv", "text/csv", "text/plain"):
            # CSV must be printable text without null bytes or binary executable headers
            if b"\x00" in content[:2048] or content.startswith(b"MZ") or content.startswith(b"\x7fELF"):
                return False
            return True

        if exp in ("svg", "image/svg+xml"):
            # SVG validated via sanitize_svg
            return True

        return True

    @classmethod
    def sanitize_svg(cls, svg_bytes: bytes) -> bytes:
        """
        Sanitize SVG content against Cross-Site Scripting (XSS), XML External Entity (XXE) injection,
        embedded scripts, event handlers, and unauthorized resource embedding.
        """
        try:
            svg_text = svg_bytes.decode("utf-8", errors="replace")
        except Exception:
            raise ValidationError(message="SVG content could not be decoded as valid UTF-8", code="INVALID_SVG")

        # 1. Reject XXE entity expansions
        if re.search(r'<!ENTITY', svg_text, re.IGNORECASE) or re.search(r'SYSTEM\s+["\']', svg_text, re.IGNORECASE):
            raise ValidationError(
                message="SVG contains forbidden XML external entity (XXE) declarations",
                code="SVG_XXE_DETECTED",
            )

        # 2. Reject explicit <script> tags
        if re.search(r'<\s*script\b[^>]*>', svg_text, re.IGNORECASE):
            raise ValidationError(
                message="SVG contains prohibited executable <script> tags",
                code="SVG_SCRIPT_DETECTED",
            )

        # 3. Strip dangerous tags: iframe, embed, object, foreignObject, applet
        dangerous_tags = [r'<\s*iframe\b[^>]*>.*?<\s*/\s*iframe\s*>',
                          r'<\s*embed\b[^>]*>',
                          r'<\s*object\b[^>]*>.*?<\s*/\s*object\s*>',
                          r'<\s*foreignObject\b[^>]*>.*?<\s*/\s*foreignObject\s*>',
                          r'<\s*applet\b[^>]*>.*?<\s*/\s*applet\s*>']
        for pattern in dangerous_tags:
            svg_text = re.sub(pattern, "", svg_text, flags=re.IGNORECASE | re.DOTALL)

        # 4. Strip JavaScript event handlers (e.g. onload, onerror, onclick, onmouseover)
        svg_text = re.sub(r'\bon\w+\s*=\s*(["\']).*?\1', '', svg_text, flags=re.IGNORECASE)
        svg_text = re.sub(r'\bon\w+\s*=\s*[^>\s]+', '', svg_text, flags=re.IGNORECASE)

        # 5. Strip javascript: and vbscript: URI schemes
        svg_text = re.sub(r'href\s*=\s*(["\'])\s*(javascript|vbscript|data):.*?\1', 'href=""', svg_text, flags=re.IGNORECASE)

        return svg_text.encode("utf-8")

    @classmethod
    def validate_zip_archive(
        cls,
        zip_bytes: bytes,
        max_files: Optional[int] = None,
        max_total_size_mb: Optional[int] = None,
        max_ratio: float = 100.0,
    ) -> List[str]:
        """
        Inspect and validate ZIP archive against Zip Slip path traversal attacks
        and Zip Bomb resource exhaustion denial-of-service attacks.
        Returns list of safe member filenames.
        """
        max_f = max_files or settings.MAX_ZIP_EXTRACT_FILES
        max_sz = (max_total_size_mb or settings.MAX_ZIP_EXTRACT_SIZE_MB) * 1024 * 1024

        try:
            zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
        except zipfile.BadZipFile:
            raise ValidationError(message="Uploaded file is not a valid ZIP archive", code="INVALID_ZIP")

        infolist = zf.infolist()
        if len(infolist) > max_f:
            raise ValidationError(
                message=f"ZIP archive contains {len(infolist)} files, exceeding limit of {max_f}",
                code="ZIP_TOO_MANY_FILES",
            )

        total_uncompressed = 0
        safe_names = []

        for info in infolist:
            # 1. Zip Slip Path Traversal Check
            filename = info.filename
            if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
                raise ValidationError(
                    message=f"ZIP contains unsafe path traversal filename: {filename}",
                    code="ZIP_SLIP_ATTACK_DETECTED",
                )
            if re.match(r'^[a-zA-Z]:', filename):  # Windows drive letter
                raise ValidationError(
                    message=f"ZIP contains absolute drive path: {filename}",
                    code="ZIP_SLIP_ATTACK_DETECTED",
                )

            # 2. Zip Bomb Compression Ratio Check
            comp_size = info.compress_size or 1
            ratio = info.file_size / comp_size
            if ratio > max_ratio and info.file_size > 1024 * 1024:
                raise ValidationError(
                    message=f"ZIP entry '{filename}' has suspicious compression ratio {ratio:.1f}:1 (Zip Bomb protection)",
                    code="ZIP_BOMB_DETECTED",
                )

            total_uncompressed += info.file_size
            if total_uncompressed > max_sz:
                raise ValidationError(
                    message=f"ZIP extracted content exceeds safety limit of {max_sz // (1024 * 1024)}MB",
                    code="ZIP_BOMB_EXCEEDED_SIZE",
                )

            safe_names.append(filename)

        return safe_names
