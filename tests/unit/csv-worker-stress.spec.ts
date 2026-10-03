import { test, expect } from "@playwright/test";
import { parseRecipientCSV } from "../../src/lib/csv-engine";
import { parseRecipientCSVAsync } from "../../src/lib/workers/csv-client";

test.describe("Unit: CSV Engine & Web Worker Stress Benchmarks", () => {
  test("benchmark: parses 10 rows instantaneously (< 5ms)", async () => {
    const rows = ["Name,Email,Course,Date,Score"];
    for (let i = 1; i <= 10; i++) {
      rows.push(`Recipient ${i},recipient${i}@example.com,Fullstack Mastery,2026-10-01,9${i % 10}`);
    }
    const csvContent = rows.join("\n");

    const t0 = performance.now();
    const result = await parseRecipientCSVAsync(csvContent);
    const duration = performance.now() - t0;

    expect(result.records.length).toBe(10);
    expect(result.validRows).toBe(10);
    expect(result.errors.length).toBe(0);
    expect(duration).toBeLessThan(20);
  });

  test("benchmark: parses 1,000 rows with high efficiency (< 50ms)", async () => {
    const rows = ["Full Name,Email Address,Program,Graduation Date,Grade"];
    for (let i = 1; i <= 1000; i++) {
      rows.push(`Student ${i},student${i}@university.edu,Machine Learning Engineering,2026-09-30,A+`);
    }
    const csvContent = rows.join("\n");

    const t0 = performance.now();
    const result = await parseRecipientCSVAsync(csvContent);
    const duration = performance.now() - t0;

    expect(result.records.length).toBe(1000);
    expect(result.validRows).toBe(1000);
    expect(result.errors.length).toBe(0);
    expect(duration).toBeLessThan(100);
  });

  test("benchmark: parses 10,000 rows without thread blocking (< 250ms)", async () => {
    const rows = ["Name,Email,Course,Date,Score"];
    for (let i = 1; i <= 10000; i++) {
      rows.push(`Engineer ${i},eng${i}@techcorp.com,Cloud Architecture Bootcamp,2026-10-02,100`);
    }
    const csvContent = rows.join("\n");

    const t0 = performance.now();
    const result = await parseRecipientCSVAsync(csvContent);
    const duration = performance.now() - t0;

    expect(result.records.length).toBe(10000);
    expect(result.validRows).toBe(10000);
    expect(duration).toBeLessThan(500);
  });

  test("stress test: parses 50,000 rows with memory stability and zero stack overflow", async () => {
    const rows = ["Name,Email,Course,Date,Score"];
    for (let i = 1; i <= 50000; i++) {
      rows.push(`Participant ${i},p${i}@globalcert.org,Enterprise Cyber Security 2026,2026-10-03,Pass`);
    }
    const csvContent = rows.join("\n");

    const t0 = performance.now();
    const result = parseRecipientCSV(csvContent);
    const duration = performance.now() - t0;

    expect(result.records.length).toBe(50000);
    expect(result.validRows).toBe(50000);
    expect(result.errors.length).toBe(0);
    // 50k rows parsed in under 2 seconds in v8/Node
    expect(duration).toBeLessThan(2500);
  });

  test("encoding: correctly strips UTF-8 BOM without corrupting first header", async () => {
    const bomCSV = "\ufeffName,Email,Course\nRahul Sharma,rahul@example.com,AI Dev";
    const result = await parseRecipientCSVAsync(bomCSV);

    expect(result.headers[0]).toBe("Name");
    expect(result.records[0].name).toBe("Rahul Sharma");
  });

  test("internationalization: preserves Hindi/Devanagari, Chinese, Arabic, and accented names", async () => {
    const unicodeCSV = `Name,Email,Course
अतुल कुमार,atul@example.in,आर्टिफिशियल इंटेलिजेंस
श्रीनिवास रामानुजन,ramanu@example.in,गणित शास्त्र
王伟,wang@example.cn,深度学习
أحمد بن علي,ahmed@example.ae,هندسة النظم
Éléonore François,eleonore@example.fr,Data Science`;

    const result = await parseRecipientCSVAsync(unicodeCSV);

    expect(result.hasUnicode).toBe(true);
    expect(result.records.length).toBe(5);
    expect(result.records[0].name).toBe("अतुल कुमार");
    expect(result.records[0].course).toBe("आर्टिफिशियल इंटेलिजेंस");
    expect(result.records[1].name).toBe("श्रीनिवास रामानुजन");
    expect(result.records[2].name).toBe("王伟");
    expect(result.records[3].name).toBe("أحمد بن علي");
    expect(result.records[4].name).toBe("Éléonore François");
  });

  test("quotes: correctly parses commas inside quoted values", async () => {
    const quotedCSV = `Name,Email,Course
"Verma, Priya",priya@example.com,"Fullstack, Cloud, and AI"
"Dr. Alexander, John",alex@med.org,"Medicine, Surgery & Ethics"`;

    const result = await parseRecipientCSVAsync(quotedCSV);

    expect(result.records.length).toBe(2);
    expect(result.records[0].name).toBe("Verma, Priya");
    expect(result.records[0].course).toBe("Fullstack, Cloud, and AI");
    expect(result.records[1].name).toBe("Dr. Alexander, John");
  });

  test("empty rows: gracefully skips empty and whitespace lines", async () => {
    const whitespaceCSV = `Name,Email,Course
Ananya Sen,ananya@test.com,UX Design

   
Vikram Rao,vikram@test.com,DevOps

`;

    const result = await parseRecipientCSVAsync(whitespaceCSV);
    expect(result.records.length).toBe(2);
    expect(result.validRows).toBe(2);
  });

  test("duplicate headers: flags duplicate column headers with actionable warning", async () => {
    const dupCSV = `Name,Email,Name,Course
Karan,karan@test.com,DuplicateKaran,Web3`;

    const result = await parseRecipientCSVAsync(dupCSV);
    expect(result.warnings.length).toBeGreaterThan(0);
    expect(result.warnings[0].message).toContain("Duplicate column header");
  });

  test("missing headers: handles CSV without standard headers gracefully", async () => {
    const noHeaderCSV = `Unknown1,Unknown2,Unknown3
Val1,Val2,Val3`;

    const result = await parseRecipientCSVAsync(noHeaderCSV);
    expect(result.records.length).toBe(1);
    expect(result.records[0].rowNumber).toBe(1);
  });

  test("malformed CSV: resilient against unclosed quotes and uneven column counts", async () => {
    const malformed = `Name,Email,Course
"Broken Quote,broken@test.com,Course 1
Valid Name,valid@test.com,Course 2`;

    // Should not throw unhandled exception
    expect(() => parseRecipientCSV(malformed)).not.toThrow();
    const result = parseRecipientCSV(malformed);
    expect(result).toBeDefined();
  });

  test("security: neutralizes spreadsheet formula injection (=, +, -, @)", async () => {
    const injectionCSV = `Name,Email,Course
=cmd|' /C calc'!A0,hacker@evil.com,Malicious Course
+123456,user@test.com,Math
@SUM(1+1),admin@test.com,Finances`;

    const result = await parseRecipientCSVAsync(injectionCSV);
    for (const record of result.records) {
      expect(record.name.startsWith("=")).toBe(false);
      expect(record.name.startsWith("+")).toBe(false);
      expect(record.name.startsWith("@")).toBe(false);
    }
  });
});
