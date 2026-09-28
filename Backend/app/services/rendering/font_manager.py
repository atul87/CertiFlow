"""
FontManager — P3.12 / P3.13

Resolves font family + size + weight + italic requests to a PIL ImageFont.
Strategy (in order):
  1. Bundled fonts directory inside the service: storage/fonts/
  2. Pillow default (always succeeds — guarantees no crash)

Never fails silently — always returns a usable font.
"""
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Tuple
from PIL import ImageFont

logger = logging.getLogger(__name__)

# Directory where bundled TTF/OTF fonts live (relative to repo root)
_FONTS_DIR = Path(os.environ.get("FONTS_DIR", "storage/fonts"))

# Map common CSS-style families to stored filenames.
# Files are expected at  <_FONTS_DIR>/<family>/<weight>/<italic>.ttf
# but we also support flat structure: <_FONTS_DIR>/<filename>.ttf
_FAMILY_MAP: Dict[str, Dict[str, str]] = {
    # fallback filenames when exact weight/italic variant is missing
    "default": {
        "regular": "NotoSans-Regular.ttf",
        "bold": "NotoSans-Bold.ttf",
    },
}

# In-memory cache:  (family, size, weight, italic) -> ImageFont
_FONT_CACHE: Dict[Tuple, ImageFont.ImageFont] = {}


def _find_font_file(family: str, weight: int, italic: bool) -> Optional[Path]:
    """
    Try to locate a TTF/OTF font file for the given family/weight/italic.
    Searches <_FONTS_DIR>/<family>/ with multiple naming conventions.
    """
    base = _FONTS_DIR
    if not base.is_dir():
        return None

    # Normalise family name for filesystem lookup
    family_clean = family.replace(" ", "").replace("-", "").lower()

    weight_label = "Bold" if weight >= 600 else "SemiBold" if weight >= 500 else "Regular"
    italic_label = "Italic" if italic else ""
    variant = f"{weight_label}{italic_label}"

    candidates = [
        base / f"{family}-{variant}.ttf",
        base / f"{family}-{variant}.otf",
        base / f"{family_clean}-{variant.lower()}.ttf",
        base / f"{family}{variant}.ttf",
        base / f"{family}-Regular.ttf",
        base / f"{family}.ttf",
        base / f"{family_clean}.ttf",
    ]
    for c in candidates:
        if c.is_file():
            logger.debug("FontManager: resolved %s -> %s", family, c)
            return c
    return None


def load_font(
    family: str = "Inter",
    size: int = 48,
    weight: int = 400,
    italic: bool = False,
) -> ImageFont.ImageFont:
    """
    Return a PIL ImageFont for the requested family/size/weight/italic.
    Falls back gracefully: bundled file → Pillow default bitmap.
    Never raises — always returns a valid font object.
    """
    cache_key = (family, size, weight, italic)
    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]

    font_path = _find_font_file(family, weight, italic)
    font: ImageFont.ImageFont

    if font_path:
        try:
            font = ImageFont.truetype(str(font_path), size=size)
            _FONT_CACHE[cache_key] = font
            return font
        except Exception as exc:
            logger.warning("FontManager: failed to load %s at %s — %s", family, font_path, exc)

    # Try Pillow's built-in default with size support (Pillow >= 9.2.0)
    try:
        font = ImageFont.load_default(size=size)
    except TypeError:
        font = ImageFont.load_default()

    _FONT_CACHE[cache_key] = font
    return font


def clear_cache() -> None:
    """Useful in tests to reset the font cache."""
    _FONT_CACHE.clear()
