import type { CSVParseResult } from "../csv-engine";
import { parseRecipientCSV } from "../csv-engine";
import type { CSVWorkerRequest, CSVWorkerResponse } from "./csv.worker";

/**
 * Executes CSV parsing off the main UI thread via Web Worker when supported in browser,
 * avoiding UI thread locking on 10,000+ line recipient rosters.
 * Falls back gracefully to in-thread parsing for SSR, Node.js, and test runners.
 */
export async function parseRecipientCSVAsync(csvString: string): Promise<CSVParseResult> {
  if (typeof window !== "undefined" && typeof Worker !== "undefined") {
    return new Promise<CSVParseResult>((resolve, reject) => {
      try {
        const workerUrl = new URL("./csv.worker.ts", window.location.href);
        const worker = new Worker(workerUrl);

        worker.onmessage = (event: MessageEvent<CSVWorkerResponse>) => {
          worker.terminate();
          if (event.data.type === "PARSE_CSV_SUCCESS" && event.data.result) {
            resolve(event.data.result);
          } else {
            reject(new Error(event.data.error || "CSV Worker failed parsing"));
          }
        };

        worker.onerror = () => {
          worker.terminate();
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
        try {
          resolve(parseRecipientCSV(csvString));
        } catch (fallbackErr) {
          reject(fallbackErr);
        }
      }
    });
  }

  // Graceful fallback for Node.js / Playwright / SSR
  return Promise.resolve(parseRecipientCSV(csvString));
}
