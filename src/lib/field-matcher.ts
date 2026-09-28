export interface MatchResult {
  tag: string;
  matchedHeader: string | null;
  confidence: number;
  matchType: "exact" | "normalized" | "alias" | "fuzzy" | "auto_system" | "none";
}

const TAG_ALIASES: Record<string, string[]> = {
  "{{NAME}}": [
    "full name",
    "name",
    "student name",
    "attendee name",
    "attendee",
    "participant name",
    "participant",
    "recipient name",
    "recipient",
    "candidate",
  ],
  "{{COURSE}}": [
    "course",
    "course title",
    "course name",
    "program",
    "event",
    "workshop",
    "topic",
    "seminar",
    "track",
    "subject",
  ],
  "{{DATE}}": [
    "completion date",
    "issue date",
    "date",
    "awarded on",
    "event date",
    "graduated on",
    "awarded date",
  ],
  "{{SCORE}}": [
    "score",
    "grade",
    "percentage",
    "marks",
    "result",
    "distinction",
    "rank",
  ],
  "{{EMAIL}}": [
    "email",
    "recipient email",
    "student email",
    "contact email",
    "e-mail",
  ],
  "{{CERTIFICATE_ID}}": [
    "certificate id",
    "credential id",
    "cert id",
    "uuid",
    "unique id",
    "hash",
  ],
};

/**
 * Matches template placeholders to available CSV column headers
 */
export function matchColumnsToTags(
  availableHeaders: string[],
  tags: string[]
): Record<string, MatchResult> {
  const results: Record<string, MatchResult> = {};
  const usedHeaders = new Set<string>();

  for (const tag of tags) {
    const rawTagKey = tag.replace(/^\{\{|\}\}$/g, "").toLowerCase();

    // 1. Special system generator field: CERTIFICATE_ID
    if (tag === "{{CERTIFICATE_ID}}") {
      const explicitHeader = availableHeaders.find(
        (h) => !usedHeaders.has(h) && (h.toLowerCase().includes("certificate") || h.toLowerCase() === "id")
      );
      if (explicitHeader) {
        usedHeaders.add(explicitHeader);
        results[tag] = {
          tag,
          matchedHeader: explicitHeader,
          confidence: 95,
          matchType: "alias",
        };
      } else {
        results[tag] = {
          tag,
          matchedHeader: "AUTO_GENERATED_HASH",
          confidence: 100,
          matchType: "auto_system",
        };
      }
      continue;
    }

    // 2. Exact match
    const exact = availableHeaders.find(
      (h) => !usedHeaders.has(h) && h === tag
    );
    if (exact) {
      usedHeaders.add(exact);
      results[tag] = { tag, matchedHeader: exact, confidence: 100, matchType: "exact" };
      continue;
    }

    // 3. Case-insensitive / Normalized match
    const normalized = availableHeaders.find(
      (h) => !usedHeaders.has(h) && h.trim().toLowerCase() === rawTagKey
    );
    if (normalized) {
      usedHeaders.add(normalized);
      results[tag] = { tag, matchedHeader: normalized, confidence: 98, matchType: "normalized" };
      continue;
    }

    // 4. Alias Dictionary match
    const aliases = TAG_ALIASES[tag] || [];
    let aliasFound: string | null = null;
    for (const alias of aliases) {
      const match = availableHeaders.find(
        (h) => !usedHeaders.has(h) && h.trim().toLowerCase() === alias
      );
      if (match) {
        aliasFound = match;
        break;
      }
    }
    if (aliasFound) {
      usedHeaders.add(aliasFound);
      results[tag] = { tag, matchedHeader: aliasFound, confidence: 95, matchType: "alias" };
      continue;
    }

    // 5. Token Substring / Fuzzy match
    const fuzzy = availableHeaders.find((h) => {
      if (usedHeaders.has(h)) return false;
      const lowerH = h.toLowerCase();
      return aliases.some((a) => lowerH.includes(a) || a.includes(lowerH));
    });
    if (fuzzy) {
      usedHeaders.add(fuzzy);
      results[tag] = { tag, matchedHeader: fuzzy, confidence: 85, matchType: "fuzzy" };
      continue;
    }

    // 6. No match found
    results[tag] = { tag, matchedHeader: null, confidence: 0, matchType: "none" };
  }

  return results;
}
