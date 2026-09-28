# CertiFlow — Portable Digital Credential & Certificate SaaS Platform

CertiFlow is an enterprise-grade SaaS platform for generating, managing, verifying, and distributing high-fidelity certificates and machine-readable portable digital credentials (**W3C Verifiable Credentials Data Model v2.0** and **1EdTech Open Badges 3.0**).

---

## 1. System Architecture: P0 to P11

```text
                                  CertiFlow SaaS
                                        │
             ┌──────────────────────────┴──────────────────────────┐
             │                                                     │
             ▼                                                     ▼
      PDF Certificate                                      Digital Credential
      (Human-Readable)                                    (Machine-Readable)
             │                                                     │
             ├── P1  Template Canvas Engine                        ├── P11.2 Issuer Profiles
             ├── P2  CSV / Excel Intelligent Ingest                ├── P11.3 Achievement Models
             ├── P3  High-DPI PDF & PNG Renderer                   ├── P11.6 Open Badges 3.0
             ├── P4  Distributed ARQ Background Workers            ├── P11.7 W3C Verifiable Credentials
             ├── P5  Instant QR Verification & SHA-256             ├── P11.8 Ed25519 Cryptographic Signatures
             ├── P6  Transactional Email & Notifications           ├── P11.10 Real-time Status Registry
             ├── P7  Analytics Dashboard & Aggregation             ├── P11.13 Public Verification & Privacy
             ├── P8  Teams, RBAC, API Keys & Webhooks              └── P11.16 Wallet Integration & Sharing
             ├── P9  Security Hardening & Rate Limiting
             └── P10 Multi-Tenant Billing & Usage Metering
```

---

## 2. Complete Phase Walkthrough (P0 to P11)

### **Phase 0 — Core Backend & Architecture Foundation**
* **Framework**: FastAPI (async ASGI), Python 3.13, Pydantic v2.
* **Database**: MongoDB (Motor async driver) with compound, sparse, and unique indexes.
* **Authentication**: Argon2 password hashing, short-lived JWT access tokens, cryptographically random refresh tokens stored as SHA-256 hashes.
* **Security & Observability**: Correlation Request IDs (`req_...`), security headers (`nosniff`, `DENY`, `HSTS`), centralized error handlers with standard envelope responses (`APIResponse`).

### **Phase 1 — Template Design & Publishing Engine**
* **Canvas Coordinates**: Millimeter and pixel coordinate system with standard DPI calculations.
* **Template Elements**: Text placeholders, dynamic variables, logos/images, dynamic QR codes, shapes, barcodes.
* **Versioning & Immutability**: Semantic versioning (`v1`, `v2`, ...). Published versions are strictly immutable to guarantee certificate reproducibility.
* **Custom Typography**: Built-in and custom font upload registry (`.ttf`, `.otf`, `.woff`, `.woff2`) with automated CSS font-face registration.

### **Phase 2 — CSV/Excel Intelligence & Data Profiling**
* **Multi-Format Parsers**: Streaming CSV parser with automatic delimiter detection (`comma`, `semicolon`, `tab`), auto-encoding detection (UTF-8, UTF-16, Latin-1, CP1252), and Excel `.xlsx` parser (safely rejecting `.xlsm` macros).
* **AI/Heuristic Field Matcher**: Levenshtein distance and synonym matching automatically maps file columns (`Student Name`, `Email Address`, `Course Title`) to template fields.
* **Data Profiler & Validator**: Validates rows against required schema rules, validates email syntaxes, flags duplicates, and exports actionable error CSV reports.

### **Phase 3 — Certificate Rendering Engine**
* **Vector & Pixel Pipeline**: SVG templating with Playwright / CairoSVG / ReportLab / Skia rendering engine.
* **Print Quality**: Exact 300 DPI high-resolution PDF rendering with CMYK/RGB color fidelity.
* **Previews**: Fast, lightweight PNG thumbnail generation with downscaled dimensions for dashboard previews.
* **Identifiers**: Unique sequential certificate numbers (`CERT-YYYY-XXXXX`) and 8-12 character alphanumeric verification codes.
* **Cryptographic Tamper Detection**: Deterministic SHA-256 file hashing computed at render time and recorded in MongoDB.

### **Phase 4 — Distributed Bulk Issuance & Worker Queue**
* **Queue Engine**: ARQ async worker pool powered by Redis with connection timeouts, retries, and dead-letter queues.
* **Chunking & Concurrency**: Jobs split into manageable batches with atomic Redis progress counters (`completed_count`, `failed_count`, `percent_complete`).
* **Idempotency**: Global idempotency keys prevent duplicate generation or double billing.
* **Bulk Export**: In-memory streaming ZIP archive builder for one-click downloading of thousands of generated PDFs.

### **Phase 5 — QR Verification & Lifecycle Management**
* **Instant QR Resolution**: Dynamic QR code embedded on every certificate resolves to public verification URL.
* **Physical Integrity Verification**: Public upload endpoint recalculates SHA-256 hash of an uploaded PDF and matches it against the stored hash to detect modified or forged documents.
* **Status Lifecycle**: `active` $\to$ `suspended` $\to$ `revoked` $\to$ `restored`.
* **Privacy Controls**: Public verification endpoint reveals recipient display name and certificate metadata while strictly redacting email addresses, phone numbers, and internal database IDs.
* **Audit Timeline**: Chronological event logs for all lifecycle transitions.

### **Phase 6 — Email Delivery & Notifications**
* **Adapters**: Pluggable provider architecture with SMTP, SendGrid, Amazon SES, and Mock test provider.
* **Template Engine**: Jinja2 email templates supporting dynamic variables (`{{recipient_name}}`, `{{certificate_url}}`, `{{verification_code}}`).
* **Signed Download URLs**: HMAC-SHA256 signed download tokens with time-limited expirations for secure 1-click recipient downloads.
* **Deliverability & Suppressions**: Automated bounce and complaint processing with recipient suppression lists.

### **Phase 7 — Analytics Dashboard & Reporting**
* **Aggregations**: Real-time and scheduled daily background aggregation of issuance velocity, verification events, delivery rates, and device/browser breakdowns.
* **Time-Series Metrics**: Trends over 7, 30, and 90-day rolling windows.
* **Activity Feeds**: Audit trails for team and organization operations.
* **Automated Reports**: Background generation of CSV and PDF analytics reports.

### **Phase 8 — Multi-Tenant Teams, RBAC, Developer API & Webhooks**
* **Multi-Tenancy**: Complete isolation by `organization_id` across all queries and operations.
* **Fine-Grained RBAC**: 30+ system permissions with pre-built roles (`owner`, `admin`, `member`, `viewer`) and custom role builder.
* **Developer API Keys**: Scoped API keys (`ck_live_...`) with permission sets, prefix indexing, and SHA-256 secret hashing.
* **Outbound Webhooks**: Event-driven webhook notifications signed with HMAC-SHA256 headers (`X-Signature-SHA256`) and exponential backoff retry worker.

### **Phase 9 — Production Hardening & Security**
* **Rate Limiting**: Sliding-window rate limiters protecting authentication, public verification, and export endpoints.
* **SSRF Protection**: Strict URL validator rejecting loopback addresses (`127.0.0.1`), private RFC 1918 subnets, link-local addresses, and cloud metadata IPs (`169.254.169.254`).
* **Content Safety**: Magic byte inspection and XML/SVG entity sanitization to block XXE attacks and embedded scripts.

### **Phase 10 — Production SaaS, Subscriptions & Metering**
* **Subscription Tiers**: `Starter`, `Professional`, `Enterprise` with trial periods and billing cycles.
* **Entitlement Engine**: Hard-quota and soft-quota enforcement before executing operations.
* **Metered Billing**: Atomic monthly counters for `certificates_generated`, `credentials_issued`, `emails_sent`, and `storage_bytes`.
* **Inbound Billing Webhooks**: Stripe webhook handlers with HMAC verification, replay attack prevention, and automatic plan provisioning.
* **SaaS Admin APIs**: Organization suspension, quota overrides, and platform KPI analytics.

### **Phase 11 — Open Badges 3.0 & W3C Verifiable Credentials**
* **Decoupled Entities**: Separate `issuer_profiles`, `achievements`, and `credentials` collections.
* **Ed25519 Cryptography**: Asymmetric cryptographic signatures with keys encrypted at rest using Fernet.
* **RFC 8785 Canonicalization**: Deterministic JSON normalization for cross-platform signature verification.
* **W3C Data Integrity**: `Ed25519Signature2020` proof blocks.
* **Dual Representation**:
  - Open Badges 3.0: `GET /api/v1/public/credentials/{id}/badge`
  - W3C VC v2.0: `GET /api/v1/public/credentials/{id}/vc`
* **Real-time Status Registry**: Synchronized revocation between certificates and credentials.
* **Decentralized Verifier**: `POST /api/v1/public/credentials/verify` accepts arbitrary external payloads and cryptographically verifies them without needing platform database records.

---

## 3. Quick Start & Running Locally

### Backend Setup
```bash
cd Backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Configuration
Create `Backend/.env`:
```env
APP_NAME=CertiFlow
APP_ENV=development
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=certiflow
JWT_SECRET_KEY=change-this-to-a-very-long-and-secure-random-secret-key-32bytes
ENCRYPTION_KEY=gAAAAABl... # 32-byte url-safe base64 key
APP_BASE_URL=http://localhost:3000
BASE_URL=http://localhost:8000
```

### Launch Development Server
```bash
uvicorn app.main:app --reload --port 8000
```

API Documentation will be available at:
* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 4. Automated Test Suite (247 Tests Passing)

```bash
cd Backend

# 1. Pure Unit Tests (Fast, in-memory, no DB required)
.venv\Scripts\pytest -m no_db

# 2. P11 Digital Credentials & Cryptography Suites
.venv\Scripts\pytest tests/unit/test_credentials_and_cryptography.py tests/integration/test_credentials_and_issuance.py tests/security/test_credential_security.py -v

# 3. Grand End-to-End Complete Journey (P0 to P11)
.venv\Scripts\pytest tests/integration/test_full_e2e_p0_to_p11.py -v

# 4. Entire Platform Test Suite (All 247 tests passing)
.venv\Scripts\pytest
```

---

## 5. Technology Stack Summary

| Layer | Technologies |
|---|---|
| **Backend API** | FastAPI, Starlette, Uvicorn, Python 3.13 |
| **Database** | MongoDB 7.0+, Motor (Async Driver), PyMongo |
| **Queue & Cache** | Redis 7.0+, ARQ (Async Redis Queue) |
| **Cryptography** | `cryptography` (Ed25519, Fernet, X.509/SPKI), Argon2-cffi, PyJWT |
| **Document Rendering** | Playwright, ReportLab, CairoSVG, PyMuPDF, Pillow, QRCodegen |
| **Data Parsing** | OpenPyXL, Python CSV, Charset-Normalizer |
| **Standards** | W3C Verifiable Credentials Data Model v2.0, 1EdTech Open Badges 3.0, RFC 8785 (JCS) |
