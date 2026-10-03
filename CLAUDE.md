# CertiFlow — AI Agent & Developer Quick Reference (CLAUDE.md)

@AGENTS.md

## 1. Project Overview & Architecture
CertiFlow is an enterprise SaaS platform for bulk certificate generation and portable digital credentials adhering to **W3C Verifiable Credentials Data Model v2.0** and **1EdTech Open Badges 3.0**.

- **Frontend**: Next.js 16 (App Router + Turbopack), React 19, Tailwind CSS v4, Zustand v5 (`src/`)
- **Backend**: FastAPI 0.115 (Python 3.12+), Motor (MongoDB 7.0), Redis 7.0 + ARQ (`Backend/`)
- **Test Harness**: 375 tests passing (247 Pytest, 114 Playwright E2E, 14 Auth E2E, 0 TypeScript errors)

---

## 2. Essential Commands

### Starting Development Servers
```powershell
# 1. Backend (FastAPI API Gateway on http://127.0.0.1:8000)
cd e:\Certificate\Backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 2. Background Queue Worker (ARQ Redis Worker)
cd e:\Certificate\Backend
.\.venv\Scripts\Activate.ps1
arq app.queue.worker.WorkerSettings

# 3. Frontend (Next.js 16 Turbopack on http://localhost:3000)
cd e:\Certificate
npm run dev
```

### Running Test Suites
```powershell
# Run all backend unit, integration, and security tests (247 tests)
cd e:\Certificate\Backend
.\.venv\Scripts\Activate.ps1
pytest tests -v

# Run frontend Playwright end-to-end suite (114 tests)
cd e:\Certificate
npm run test:e2e

# Run dedicated authentication Playwright suite (14 tests)
npx playwright test tests/e2e/auth-system.spec.ts --project=chromium

# TypeScript compilation check (Strict mode, must always be 0 errors)
npm run typecheck

# Linting
npm run lint
```

---

## 3. Critical Architectural Rules & Invariants

1. **Separation of Authority**:
   - Browser Web Workers handle client-side CSV parsing, 5-tier fuzzy column mapping, font bounding calculations, and 60 FPS SVG preview.
   - Server ARQ workers handle authoritative tasks: high-DPI PDF generation (ReportLab), Ed25519 digital signatures, SHA-256 PDF sealing, and SMTP email distribution.
   - **Never** render batches of final PDF certificates in the client browser.

2. **Dual-Authentication Engine**:
   - Frontend API client (`src/lib/api/client.ts`) attaches both HttpOnly cookies (`credentials: 'include'`) and `Authorization: Bearer <token>` from `tokenStorage` to bridge cross-origin port isolation between `:3000` and `:8000`.
   - The active organization ID is forwarded via `X-Organization-Id`.
   - Use `src/lib/api/auth.ts` for session persistence.

3. **RFC 6761 Email Validation Rule**:
   - Pydantic's `email-validator` strictly rejects reserved TLDs (e.g. `.test`, `.example`, `.invalid`) with HTTP 422.
   - **Always** use valid domain extensions like `@certiflow.io` or `@example.com` in tests and fixtures.

4. **Deterministic Canonicalization (RFC 8785)**:
   - When generating or verifying W3C VC or Open Badges 3.0 proofs, always canonicalize JSON payloads using `canonicalize_json()` (`Backend/app/credentials/canonicalizer.py`) before computing SHA-256 digests or Ed25519 signatures.

5. **Responsive DOM Assertions in E2E Tests**:
   - Desktop sidebar elements (`FastAPI: Connected`) are hidden on mobile viewports (`hidden md:flex`). Assert against universal main content headings (e.g. `Welcome back`) for cross-device test reliability.

---

## 4. Documentation Suite Directory

- [`docs/ARCHITECTURE.md`](file:///e:/Certificate/docs/ARCHITECTURE.md): System architecture, separation of authority, data pipelines, finite state machines, threat modeling.
- [`docs/API_REFERENCE.md`](file:///e:/Certificate/docs/API_REFERENCE.md): Complete 18-domain REST API specification, standard `APIResponse[T]` envelope, and error codes.
- [`docs/DEVELOPER_GUIDE.md`](file:///e:/Certificate/docs/DEVELOPER_GUIDE.md): Local development setup, environment variables catalog, database seeding, and testing guide.
- [`docs/STANDARDS_COMPLIANCE.md`](file:///e:/Certificate/docs/STANDARDS_COMPLIANCE.md): W3C VC v2.0, Open Badges 3.0, Ed25519, Fernet encryption, and SHA-256 PDF tamper sealing.
- [`docs/USER_AND_PRODUCT_MANUAL.md`](file:///e:/Certificate/docs/USER_AND_PRODUCT_MANUAL.md): Complete product and operator handbook covering canvas editor, data ingestion, bulk issuance, and verification.
- [`PRODUCT_COMPLETION_STATUS.md`](file:///e:/Certificate/PRODUCT_COMPLETION_STATUS.md): Current 92% readiness audit and remaining milestones.
