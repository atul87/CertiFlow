import { parseRecipientCSV, type CSVParseResult } from "../csv-engine";

export interface CSVWorkerRequest {
  type: "PARSE_CSV";
  csvContent: string;
}

export interface CSVWorkerResponse {
  type: "PARSE_CSV_SUCCESS" | "PARSE_CSV_ERROR";
  result?: CSVParseResult;
  error?: string;
}

self.addEventListener("message", (event: MessageEvent<CSVWorkerRequest>) => {
  const { type, csvContent } = event.data;
  if (type === "PARSE_CSV") {
    try {
      const result = parseRecipientCSV(csvContent);
      self.postMessage({ type: "PARSE_CSV_SUCCESS", result } as CSVWorkerResponse);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to parse CSV in worker";
      self.postMessage({
        type: "PARSE_CSV_ERROR",
        error: message,
      } as CSVWorkerResponse);
    }
  }
});
