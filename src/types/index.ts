/**
 * CertiFlow — Unified Frontend Contract Types
 * Decomposed per domain (P12.7) mirroring FastAPI P0–P11 schemas.
 */

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  has_next: boolean;
}

export * from "./auth";
export * from "./organization";
export * from "./template";
export * from "./import";
export * from "./certificate";
export * from "./issuance";
export * from "./credential";
export * from "./email";
export * from "./analytics";
export * from "./report";
export * from "./team";
export * from "./developer";
export * from "./billing";
export * from "./verification";
