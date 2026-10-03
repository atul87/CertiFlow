import type { CSVParseResult } from "../csv-engine";
import { parseRecipientCSV } from "../csv-engine";
import type { CSVWorkerRequest, CSVWorkerResponse } from "./csv.worker";

/**
 * Executes CSV parsing off the main UI thread via Web Worker when supported,
 * avoiding UI thread locking on 10,000+ line recipient rosters.
 * Falls back gracefully to in-thread parsing for SSR and test runners.
 */
export async function parseRecipientCSVAsync(csvString: string): Promise<CSVParseResult> {
  if (typeof window === "undefined" || typeof Worker === "undefined") {
    return parseRecipientCSV(csvString);
  }

  return new Promise<CSVParseResult>((resolve, reject) => {
    let worker: Worker | null = null;
    try {
      worker = new Worker(new URL("./csv.worker.ts", import.meta.url));

      worker.onmessage = (event: MessageEvent<CSVWorkerResponse>) => {
        worker?.terminate();
        if (event.data.type === "PARSE_CSV_SUCCESS" && event.data.result) {
          resolve(event.data.result);
        } else {
          reject(new Error(event.data.error || "CSV Worker failed parsing"));
        }
      };

      worker.onerror = (err) => {
        worker?.terminate();
        // Fallback to synchronous in-thread parsing
        try {
          resolve(parseRecipientCSV(csvString));
        } catch (fallbackErr) {
          reject(fallbackErr);
        }
      };

      const payload: CSVWorkerRequest = {
        type: "PARSE_CSV",
        csvContent: csvString,
      };

      worker.postMessage(payload);
    } catch {
      // Worker construction not supported in environment
      try {
        resolve(parseRecipientCSV(csvString));
      } catch (fallbackErr) {
        reject(fallbackErr);
      }
    }
  });
}
