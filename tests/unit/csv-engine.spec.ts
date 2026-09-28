import { test, expect } from "@playwright/test";
import { parseRecipientCSV } from "../../src/lib/csv-engine";

test.describe("Unit: CSV Engine", () => {
  test("handles 0 rows (header only)", () => {
    const csv = "Name,Course,Date,Score,Email\n";
    const result = parseRecipientCSV(csv);

    expect(result.headers).toEqual(["Name", "Course", "Date", "Score", "Email"]);
    expect(result.totalRows).toBe(0);
    expect(result.validRows).toBe(0);
    expect(result.records).toHaveLength(0);
    expect(result.errors).toHaveLength(0);
  });

  test("handles completely empty string", () => {
    const result = parseRecipientCSV("");
    expect(result.totalRows).toBe(0);
    expect(result.records).toHaveLength(0);
  });

  test("parses single valid record correctly", () => {
    const csv = "Name,Course,Date,Score,Email\nAtul Kumar,AI Engineering,September 28 2026,98%,atul@example.com";
    const result = parseRecipientCSV(csv);

    expect(result.totalRows).toBe(1);
    expect(result.validRows).toBe(1);
    expect(result.records[0]).toMatchObject({
      rowNumber: 1,
      name: "Atul Kumar",
      course: "AI Engineering",
      date: "September 28 2026",
      score: "98%",
      email: "atul@example.com",
    });
    expect(result.errors).toHaveLength(0);
  });

  test("parses 500 rows with high performance", () => {
    const rows = ["Name,Course,Date,Score,Email"];
    for (let i = 1; i <= 500; i++) {
      rows.push(`Attendee ${i},Cloud Architecture 2026,September 28 2026,95%,attendee${i}@domain.com`);
    }
    const csv = rows.join("\n");

    const startTime = Date.now();
    const result = parseRecipientCSV(csv);
    const duration = Date.now() - startTime;

    expect(result.totalRows).toBe(500);
    expect(result.validRows).toBe(500);
    expect(result.errors).toHaveLength(0);
    expect(duration).toBeLessThan(1500); // Must parse 500 rows in <1.5s
  });

  test("scales to 10,000+ rows smoothly without stack overflow", () => {
    const rows = ["Name,Course,Date,Score,Email"];
    for (let i = 1; i <= 10000; i++) {
      rows.push(`Graduate ${i},Cybersecurity,2026-09-28,Passed,user${i}@certiflow.org`);
    }
    const csv = rows.join("\n");

    const startTime = Date.now();
    const result = parseRecipientCSV(csv);
    const duration = Date.now() - startTime;

    expect(result.totalRows).toBe(10000);
    expect(result.validRows).toBe(10000);
    expect(duration).toBeLessThan(5000); // 10,000 records parsed in < 5 seconds
  });

  test("detects duplicate recipients (duplicate emails)", () => {
    const csv = `Name,Course,Date,Score,Email
Alice Smith,Design,2026-09-28,A,alice@test.com
Bob Jones,Design,2026-09-28,B,alice@test.com`;

    const result = parseRecipientCSV(csv);
    expect(result.totalRows).toBe(2);
    expect(result.warnings.some((w) => w.message.includes("Duplicate email address"))).toBe(true);
  });

  test("identifies missing required Name and flags row error", () => {
    const csv = `Name,Course,Date,Score,Email
,Web Development,2026-09-28,90%,missing@example.com
Valid Student,Web Development,2026-09-28,95%,valid@example.com`;

    const result = parseRecipientCSV(csv);
    expect(result.totalRows).toBe(2);
    expect(result.validRows).toBe(1);
    expect(result.errors).toHaveLength(1);
    expect(result.errors[0].message).toContain("Row #1 is missing a recipient name");
  });

  test("fills sensible defaults for missing optional fields", () => {
    const csv = `Name,Course,Date,Score,Email
Jane Doe,,,,`;

    const result = parseRecipientCSV(csv);
    expect(result.totalRows).toBe(1);
    expect(result.records[0].name).toBe("Jane Doe");
    expect(result.records[0].course).toBe("Certificate Program");
    expect(result.records[0].score).toBe("Passed");
    expect(result.records[0].date).toBeTruthy();
  });

  test("flags duplicate column headers as warning", () => {
    const csv = `Name,Course,Name,Score\nAlex,Math,Alex,100`;
    const result = parseRecipientCSV(csv);

    expect(result.warnings.some((w) => w.message.includes("Duplicate column header"))).toBe(true);
  });

  test("handles empty rows and skips whitespace-only rows", () => {
    const csv = `Name,Course,Date,Score,Email
Atul Kumar,AI,2026,100,atul@test.com

   ,  ,  ,  ,   
Priya Patel,AI,2026,99,priya@test.com`;

    const result = parseRecipientCSV(csv);
    expect(result.totalRows).toBe(2);
    expect(result.records[0].name).toBe("Atul Kumar");
    expect(result.records[1].name).toBe("Priya Patel");
  });

  test("handles commas inside quoted values correctly", () => {
    const csv = `Name,Course,Date,Score,Email
"Kumar, Atul",Data Science,2026-09-28,Passed,atul@test.com
"Dr. Chandrasekharan, Vikramaditya",Quantum Computing,2026-09-28,High Distinction,dr@test.com`;

    const result = parseRecipientCSV(csv);
    expect(result.totalRows).toBe(2);
    expect(result.records[0].name).toBe("Kumar, Atul");
    expect(result.records[1].name).toBe("Dr. Chandrasekharan, Vikramaditya");
  });

  test("handles multiline quoted values gracefully", () => {
    const csv = `Name,Course,Date,Score,Email
"Atul Kumar","Advanced AI
& Deep Learning",2026-09-28,Passed,atul@test.com`;

    const result = parseRecipientCSV(csv);
    expect(result.totalRows).toBe(1);
    expect(result.records[0].course).toContain("Advanced AI\n& Deep Learning");
  });

  test("strips UTF-8 BOM properly without corrupting first header", () => {
    const bomCSV = "\uFEFFName,Course,Date,Score,Email\nAtul Kumar,AI,2026,100,atul@test.com";
    const result = parseRecipientCSV(bomCSV);

    expect(result.headers[0]).toBe("Name");
    expect(result.records[0].name).toBe("Atul Kumar");
  });

  test("supports international Unicode recipient names: Hindi, Chinese, Arabic, Accented", () => {
    const unicodeCSV = `Name,Course,Date,Score,Email
अतुल कुमार,कृत्रिम बुद्धिमत्ता,2026-09-28,उत्कृष्ट,atul.hi@test.com
张伟,人工智能,2026-09-28,优秀,zhang@test.cn
محمد بن عبدالله,علوم البيانات,2026-09-28,امتياز,mohammed@test.sa
José García Márquez,Arquitectura Cloud,2026-09-28,Sobresaliente,jose@test.es`;

    const result = parseRecipientCSV(unicodeCSV);
    expect(result.totalRows).toBe(4);
    expect(result.hasUnicode).toBe(true);
    expect(result.records[0].name).toBe("अतुल कुमार");
    expect(result.records[1].name).toBe("张伟");
    expect(result.records[2].name).toBe("محمد بن عبدالله");
    expect(result.records[3].name).toBe("José García Márquez");
  });

  test("sanitizes spreadsheet formula injection (=, +, -, @)", () => {
    const injectionCSV = `Name,Course,Date,Score,Email
=cmd|' /C calc'!A0,Hack 101,2026,100,attacker@bad.org
+123456,Math,2026,90,plus@bad.org
-dangerousFormula(),Science,2026,80,minus@bad.org
@SUM(A1:A10),Finance,2026,99,at@bad.org`;

    const result = parseRecipientCSV(injectionCSV);
    expect(result.totalRows).toBe(4);
    // Security check: Values starting with formula operators must be prepended with a quote
    expect(result.records[0].name.startsWith("'=")).toBe(true);
    expect(result.records[1].name.startsWith("'+")).toBe(true);
    expect(result.records[2].name.startsWith("'-")).toBe(true);
    expect(result.records[3].name.startsWith("'@")).toBe(true);
  });

  test("handles extremely long names without crash", () => {
    const veryLongName = "Wolfeschlegelsteinhausenbergerdorffwelchevoralternwarengrossihrenschatze".repeat(3);
    const csv = `Name,Course,Date,Score,Email\n${veryLongName},Long Course,2026,Passed,long@test.com`;

    const result = parseRecipientCSV(csv);
    expect(result.totalRows).toBe(1);
    expect(result.records[0].name.length).toBeGreaterThan(150);
  });

  test("handles malformed CSV without unhandled exception", () => {
    const malformed = `Name,Course\n"Unclosed quote row,No Date\nNormal,Course`;
    const result = parseRecipientCSV(malformed);

    expect(Array.isArray(result.records)).toBe(true);
    expect(result.totalRows).toBeGreaterThanOrEqual(1);
  });
});
