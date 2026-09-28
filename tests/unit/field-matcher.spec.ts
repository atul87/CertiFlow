import { test, expect } from "@playwright/test";
import { matchColumnsToTags } from "../../src/lib/field-matcher";

test.describe("Unit: Field Matcher Engine", () => {
  const DEFAULT_TAGS = ["{{NAME}}", "{{COURSE}}", "{{DATE}}", "{{SCORE}}", "{{CERTIFICATE_ID}}"];

  test("accurately identifies exact matches with 100% confidence", () => {
    const headers = ["{{NAME}}", "{{COURSE}}", "{{DATE}}"];
    const results = matchColumnsToTags(headers, ["{{NAME}}", "{{COURSE}}"]);

    expect(results["{{NAME}}"]).toEqual({
      tag: "{{NAME}}",
      matchedHeader: "{{NAME}}",
      confidence: 100,
      matchType: "exact",
    });
    expect(results["{{COURSE}}"]).toEqual({
      tag: "{{COURSE}}",
      matchedHeader: "{{COURSE}}",
      confidence: 100,
      matchType: "exact",
    });
  });

  test("accurately identifies normalized case-insensitive matches with 98% confidence", () => {
    const headers = ["name", "course", "date"];
    const results = matchColumnsToTags(headers, ["{{NAME}}", "{{COURSE}}"]);

    expect(results["{{NAME}}"].confidence).toBe(98);
    expect(results["{{NAME}}"].matchedHeader).toBe("name");
    expect(results["{{NAME}}"].matchType).toBe("normalized");
  });

  test("resolves aliases from dictionary with 95% confidence (Student Name, Program, Awarded On)", () => {
    const headers = ["Student Name", "Program", "Awarded On", "Grade"];
    const results = matchColumnsToTags(headers, DEFAULT_TAGS);

    expect(results["{{NAME}}"]).toEqual({
      tag: "{{NAME}}",
      matchedHeader: "Student Name",
      confidence: 95,
      matchType: "alias",
    });
    expect(results["{{COURSE}}"]).toEqual({
      tag: "{{COURSE}}",
      matchedHeader: "Program",
      confidence: 95,
      matchType: "alias",
    });
    expect(results["{{DATE}}"]).toEqual({
      tag: "{{DATE}}",
      matchedHeader: "Awarded On",
      confidence: 95,
      matchType: "alias",
    });
  });

  test("falls back to fuzzy token matching with 85% confidence", () => {
    const headers = ["Attendee Full Profile Name", "Topic Track"];
    const results = matchColumnsToTags(headers, ["{{NAME}}", "{{COURSE}}"]);

    expect(results["{{NAME}}"].confidence).toBe(85);
    expect(results["{{NAME}}"].matchType).toBe("fuzzy");
    expect(results["{{NAME}}"].matchedHeader).toBe("Attendee Full Profile Name");
  });

  test("reports 0% confidence and none type when no suitable column exists", () => {
    const headers = ["Unrelated_Column_A", "Random_Data_XYZ"];
    const results = matchColumnsToTags(headers, ["{{NAME}}"]);

    expect(results["{{NAME}}"]).toEqual({
      tag: "{{NAME}}",
      matchedHeader: null,
      confidence: 0,
      matchType: "none",
    });
  });

  test("handles {{CERTIFICATE_ID}} system generator tag automatically", () => {
    // When no CSV column has certificate ID, CertiFlow provides AUTO_GENERATED_HASH
    const headers = ["Name", "Course", "Date"];
    const results = matchColumnsToTags(headers, ["{{CERTIFICATE_ID}}"]);

    expect(results["{{CERTIFICATE_ID}}"]).toEqual({
      tag: "{{CERTIFICATE_ID}}",
      matchedHeader: "AUTO_GENERATED_HASH",
      confidence: 100,
      matchType: "auto_system",
    });
  });

  test("prefers explicit CSV column for {{CERTIFICATE_ID}} if present in spreadsheet", () => {
    const headers = ["Name", "Course", "Date", "Certificate ID"];
    const results = matchColumnsToTags(headers, ["{{CERTIFICATE_ID}}"]);

    expect(results["{{CERTIFICATE_ID}}"].matchedHeader).toBe("Certificate ID");
    expect(results["{{CERTIFICATE_ID}}"].confidence).toBe(95);
  });

  test("avoids header collision by not mapping the same header twice", () => {
    const headers = ["Name", "Other"];
    const results = matchColumnsToTags(headers, ["{{NAME}}", "{{COURSE}}"]);

    expect(results["{{NAME}}"].matchedHeader).toBe("Name");
    expect(results["{{COURSE}}"].matchedHeader).not.toBe("Name");
  });
});
