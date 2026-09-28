import Papa from "papaparse";

export interface RecipientRecord {
  rowNumber: number;
  name: string;
  course: string;
  date: string;
  score: string;
  email: string;
  raw: Record<string, string>;
}

export interface CSVParseResult {
  records: RecipientRecord[];
  headers: string[];
  totalRows: number;
  validRows: number;
  errors: { row: number; field: string; message: string }[];
  warnings: { row: number; field: string; message: string }[];
  hasUnicode: boolean;
}

/**
 * Robust CSV parser for CertiFlow bulk issuance engine
 * Supports: UTF-8 BOM, quoted commas, multiline cells, Unicode names, and formula sanitization
 */
export function parseRecipientCSV(csvString: string): CSVParseResult {
  // Strip UTF-8 BOM if present
  let cleanCSV = csvString;
  if (cleanCSV.charCodeAt(0) === 0xfeff) {
    cleanCSV = cleanCSV.slice(1);
  }

  const errors: CSVParseResult["errors"] = [];
  const warnings: CSVParseResult["warnings"] = [];
  const records: RecipientRecord[] = [];
  let headers: string[] = [];
  let hasUnicode = false;

  const parsed = Papa.parse<Record<string, string>>(cleanCSV, {
    header: true,
    skipEmptyLines: "greedy",
    transformHeader: (h) => h.trim(),
  });

  headers = parsed.meta.fields || [];

  // Inspect raw first line to detect true duplicate headers before parser auto-renames
  const firstLine = cleanCSV.split(/\r?\n/)[0] || "";
  if (firstLine) {
    const rawHeaders = firstLine.split(",").map((h) => h.trim().replace(/^["']|["']$/g, ""));
    const seenRaw = new Set<string>();
    for (const h of rawHeaders) {
      if (seenRaw.has(h.toLowerCase())) {
        warnings.push({
          row: 0,
          field: h,
          message: `Duplicate column header detected: "${h}"`,
        });
      }
      seenRaw.add(h.toLowerCase());
    }
  }

  // Find column candidates by header matching
  const findCol = (aliases: string[]) => {
    return headers.find((h) =>
      aliases.some((a) => h.toLowerCase() === a.toLowerCase())
    );
  };

  const nameCol = findCol(["Full Name", "Name", "Student Name", "Attendee", "Participant", "Recipient"]);
  const courseCol = findCol(["Course", "Program", "Event", "Workshop", "Topic"]);
  const dateCol = findCol(["Completion Date", "Date", "Issue Date", "Awarded On"]);
  const scoreCol = findCol(["Score", "Grade", "Percentage", "Result"]);
  const emailCol = findCol(["Email", "Recipient Email", "Student Email", "Contact Email"]);

  // Detect duplicate emails across records
  const seenEmails = new Set<string>();

  parsed.data.forEach((row, index) => {
    const rowNum = index + 1;

    // Check if row is entirely empty
    const values = Object.values(row).map((v) => (v ? String(v).trim() : ""));
    if (values.every((v) => v === "")) {
      return; // Skip empty rows
    }

    const rawName = nameCol ? String(row[nameCol] || "").trim() : values[0] || "";
    const rawCourse = courseCol ? String(row[courseCol] || "").trim() : values[1] || "";
    const rawDate = dateCol ? String(row[dateCol] || "").trim() : values[2] || "";
    const rawScore = scoreCol ? String(row[scoreCol] || "").trim() : values[3] || "";
    const rawEmail = emailCol ? String(row[emailCol] || "").trim() : values[4] || "";

    // Security sanitization: strip leading spreadsheet formula injection characters (=, +, -, @)
    const sanitizeValue = (val: string) => {
      if (/^[=+\-@]/.test(val)) {
        return "'" + val;
      }
      return val;
    };

    const name = sanitizeValue(rawName);
    const course = sanitizeValue(rawCourse);
    const date = sanitizeValue(rawDate);
    const score = sanitizeValue(rawScore);
    const email = rawEmail;

    // Unicode detection (e.g. Hindi, Chinese, Arabic, accented characters)
    if (/[^\u0000-\u007F]/.test(name + course)) {
      hasUnicode = true;
    }

    // Name validation
    if (!name) {
      errors.push({
        row: rowNum,
        field: "Name",
        message: `Row #${rowNum} is missing a recipient name`,
      });
    }

    // Email validation & duplicate check
    if (email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        warnings.push({
          row: rowNum,
          field: "Email",
          message: `Row #${rowNum} contains invalid email format: "${email}"`,
        });
      } else if (seenEmails.has(email.toLowerCase())) {
        warnings.push({
          row: rowNum,
          field: "Email",
          message: `Duplicate email address on row #${rowNum}: "${email}"`,
        });
      }
      seenEmails.add(email.toLowerCase());
    }

    records.push({
      rowNumber: rowNum,
      name,
      course: course || "Certificate Program",
      date: date || new Date().toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" }),
      score: score || "Passed",
      email,
      raw: row,
    });
  });

  return {
    records,
    headers,
    totalRows: records.length,
    validRows: records.filter((r) => r.name.length > 0).length,
    errors,
    warnings,
    hasUnicode,
  };
}
