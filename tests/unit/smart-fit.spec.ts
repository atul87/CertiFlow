import { test, expect } from "@playwright/test";
import { calculateSmartFontSize } from "../../src/lib/smart-fit";

test.describe("Unit: Smart-Fit Algorithm", () => {
  const BASE_SIZE = 44;
  const MIN_SIZE = 16;
  const MAX_SAFE = 24;

  test("maintains base font size for short standard Latin names", () => {
    const result = calculateSmartFontSize("Atul Kumar", BASE_SIZE, MIN_SIZE, MAX_SAFE);

    expect(result.computedFontSize).toBe(BASE_SIZE);
    expect(result.isScaledDown).toBe(false);
    expect(result.reductionPercentage).toBe(0);
  });

  test("maintains base font size for medium name within safe limit", () => {
    const result = calculateSmartFontSize("Dr. Atul Kumar", BASE_SIZE, MIN_SIZE, MAX_SAFE);

    expect(result.computedFontSize).toBe(BASE_SIZE);
    expect(result.isScaledDown).toBe(false);
  });

  test("scales down gracefully for long South Asian names (Dr. Vikramaditya Chandrasekharan)", () => {
    const name = "Dr. Vikramaditya Chandrasekharan";
    const result = calculateSmartFontSize(name, BASE_SIZE, MIN_SIZE, MAX_SAFE);

    expect(result.isScaledDown).toBe(true);
    expect(result.computedFontSize).toBeLessThan(BASE_SIZE);
    expect(result.computedFontSize).toBeGreaterThanOrEqual(MIN_SIZE);
    expect(result.reductionPercentage).toBeGreaterThan(0);
    expect(result.reductionPercentage).toBeLessThan(60);
  });

  test("applies appropriate glyph-weighting for Arabic names (محمد بن عبدالله)", () => {
    const name = "محمد بن عبدالله";
    const result = calculateSmartFontSize(name, BASE_SIZE, MIN_SIZE, MAX_SAFE);

    // Arabic glyphs have 1.4x weighting
    expect(result.effectiveLength).toBeGreaterThan(name.length);
    expect(result.computedFontSize).toBeGreaterThanOrEqual(MIN_SIZE);
  });

  test("applies appropriate glyph-weighting for Devanagari Hindi names (अतुल कुमार)", () => {
    const name = "अतुल कुमार";
    const result = calculateSmartFontSize(name, BASE_SIZE, MIN_SIZE, MAX_SAFE);

    // Devanagari characters receive 1.4x visual weighting
    expect(result.effectiveLength).toBeGreaterThan(name.length * 1.1);
    expect(result.computedFontSize).toBeGreaterThanOrEqual(MIN_SIZE);
  });

  test("clamps to minFontSize for extremely long strings without collapsing", () => {
    const extremeName = "A very very very long certificate recipient name that exceeds typical printable boundaries by far";
    const result = calculateSmartFontSize(extremeName, BASE_SIZE, MIN_SIZE, MAX_SAFE);

    expect(result.computedFontSize).toBe(MIN_SIZE);
    expect(result.isScaledDown).toBe(true);
    expect(result.reductionPercentage).toBe(Math.round(((BASE_SIZE - MIN_SIZE) / BASE_SIZE) * 100));
  });

  test("handles empty string gracefully", () => {
    const result = calculateSmartFontSize("", BASE_SIZE, MIN_SIZE, MAX_SAFE);

    expect(result.computedFontSize).toBe(BASE_SIZE);
    expect(result.isScaledDown).toBe(false);
    expect(result.reductionPercentage).toBe(0);
    expect(result.effectiveLength).toBe(0);
  });

  test("correctly scales for CJK ideographs (张伟, 诸葛孔明)", () => {
    const cjk = "诸葛孔明先生";
    const result = calculateSmartFontSize(cjk, BASE_SIZE, MIN_SIZE, 5);

    expect(result.effectiveLength).toBeGreaterThan(cjk.length);
    expect(result.isScaledDown).toBe(true);
  });
});
