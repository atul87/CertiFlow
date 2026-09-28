export interface SmartFitResult {
  computedFontSize: number;
  baseFontSize: number;
  minFontSize: number;
  isScaledDown: boolean;
  reductionPercentage: number;
  effectiveLength: number;
}

/**
 * Calculates optimal font size to prevent certificate text overflow
 * Handles Latin, Devanagari, CJK, and Arabic glyph widths
 */
export function calculateSmartFontSize(
  text: string,
  baseFontSize: number,
  minFontSize: number = 16,
  maxSafeCharacters: number = 24
): SmartFitResult {
  if (!text || text.length === 0) {
    return {
      computedFontSize: baseFontSize,
      baseFontSize,
      minFontSize,
      isScaledDown: false,
      reductionPercentage: 0,
      effectiveLength: 0,
    };
  }

  // Calculate effective glyph length with weighting for wide scripts
  let effectiveLength = 0;
  for (const char of text) {
    const code = char.codePointAt(0) || 0;
    // CJK, Devanagari, Arabic, and Emoji ranges take more visual width
    if (
      (code >= 0x4e00 && code <= 0x9fff) || // CJK Unified Ideographs
      (code >= 0x0900 && code <= 0x097f) || // Devanagari (Hindi, Sanskrit)
      (code >= 0x0600 && code <= 0x06ff)    // Arabic
    ) {
      effectiveLength += 1.4;
    } else if (char === " " || char === "." || char === "-" || char === "'") {
      effectiveLength += 0.5;
    } else if (char === char.toUpperCase() && char !== char.toLowerCase()) {
      effectiveLength += 1.2;
    } else {
      effectiveLength += 1.0;
    }
  }

  if (effectiveLength <= maxSafeCharacters) {
    return {
      computedFontSize: baseFontSize,
      baseFontSize,
      minFontSize,
      isScaledDown: false,
      reductionPercentage: 0,
      effectiveLength: Math.round(effectiveLength * 10) / 10,
    };
  }

  // Scale down proportionally
  const excess = effectiveLength - maxSafeCharacters;
  const reductionRate = 0.022; // 2.2% reduction per excess unit
  const minScale = minFontSize / baseFontSize;
  const scaleFactor = Math.max(minScale, 1 - excess * reductionRate);

  const rawComputed = Math.round(baseFontSize * scaleFactor);
  const clampedSize = Math.max(minFontSize, Math.min(baseFontSize, rawComputed));

  const reductionPercentage = Math.round(((baseFontSize - clampedSize) / baseFontSize) * 100);

  return {
    computedFontSize: clampedSize,
    baseFontSize,
    minFontSize,
    isScaledDown: clampedSize < baseFontSize,
    reductionPercentage,
    effectiveLength: Math.round(effectiveLength * 10) / 10,
  };
}
