# CertiFlow — Backend Foundation & Template Management (P0 & P1)

Enterprise FastAPI + MongoDB backend for automated certificate generation SaaS.

---

## 1. Technology Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
- **Database**: [MongoDB](https://www.mongodb.com/) (System Service / Local instance at `localhost:27017` or Atlas)
- **Async Driver**: [Motor](https://motor.readthedocs.io/) (`AsyncIOMotorClient`)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev/) + `pydantic-settings`
- **Security & Passwords**: Argon2id (`argon2-cffi`)
- **Authentication**: JWT access tokens + rotated SHA-256 hashed refresh tokens
- **Rendering & Preview**: Pillow (PIL) + QRCode
- **Testing**: `pytest` + `pytest-asyncio` + `httpx` (**45/45 automated tests passing**)
- **Containerization**: Docker + Docker Compose

---

## 2. Directory Architecture

```text
Backend/
├── app/
│   ├── main.py                  # FastAPI app factory, lifespan, CORS, error handling
│   ├── core/
│   │   ├── config.py            # Centralized Pydantic Settings
│   │   ├── database.py          # Motor AsyncIOMotorClient + startup index creation
│   │   ├── exceptions.py        # Typed application exceptions (401, 403, 404, 409, 422)
│   │   ├── logging.py           # Structured logging setup
│   │   └── security.py          # Argon2id hasher + JWT access/refresh token utils
│   ├── api/
│   │   ├── deps.py              # Auth & RBAC dependencies (get_current_user, require_role)
│   │   └── v1/
│   │       ├── router.py        # Centralized /api/v1 router
│   │       ├── auth.py          # /register, /login, /refresh, /logout, /me
│   │       ├── organizations.py # /me, PATCH /me, /me/members
│   │       ├── templates.py     # Template CRUD, versioning, publishing, duplicate, archive, assets, preview
│   │       ├── fonts.py         # System and custom font discovery
│   │       └── health.py        # /health, /health/db
│   ├── models/                  # Domain entity definitions
│   ├── schemas/
│   │   ├── auth.py              # TokenResponse, AuthMeResponse, RefreshTokenRequest
│   │   ├── common.py            # APIResponse[T], APIErrorDetail
│   │   ├── organization.py      # OrganizationResponse, OrganizationUpdate, MemberResponse
│   │   ├── user.py              # UserRegisterRequest, UserLoginRequest, UserResponse
│   │   ├── template.py          # TemplateResponse, TemplateVersionResponse, Elements, Fields, Preview
│   │   └── asset.py             # AssetResponse, FontResponse
│   ├── services/
│   │   ├── auth_service.py      # Registration, login, token rotation, logout
│   │   ├── organization_service.py # Multi-tenant org isolation & RBAC checks
│   │   ├── template_service.py  # Template lifecycle, versioning, immutability, duplicate, archive
│   │   ├── placeholder_service.py # {{placeholder}} syntax parsing, field extraction, substitution
│   │   ├── template_validator.py# Canvas bounds, coordinate validation, pre-publish rules
│   │   ├── storage_service.py   # Isolated asset filesystem storage outside MongoDB
│   │   ├── asset_service.py     # Image upload, signature validation, metadata persistence
│   │   └── preview_service.py   # High-fidelity lightweight certificate canvas rendering (PIL + QR)
│   ├── repositories/
│   │   ├── user_repository.py         # MongoDB users collection queries
│   │   ├── organization_repository.py # MongoDB organizations & members queries
│   │   ├── refresh_token_repository.py# Rotated hashed token storage
│   │   ├── audit_log_repository.py    # Audit logging for security compliance
│   │   ├── template_repository.py     # MongoDB templates collection
│   │   ├── template_version_repository.py # MongoDB template_versions collection
│   │   ├── asset_repository.py        # MongoDB assets collection
│   │   └── font_repository.py         # MongoDB fonts collection
│   └── middleware/
│       ├── request_id.py        # X-Request-ID propagation & HTTP access logging
│       └── error_handler.py     # Global exception handlers returning standardized envelopes
├── storage/                     # Isolated filesystem storage for assets outside MongoDB
├── tests/
│   ├── conftest.py              # Async test client & isolated test DB fixtures
│   ├── unit/
│   │   ├── test_config.py       # Configuration & CORS parsing tests
│   │   ├── test_security.py     # Argon2id & JWT token unit tests
│   │   ├── test_placeholders.py # Placeholder syntax, duplicate consolidation, system fields
│   │   └── test_template_validator.py # Geometry, bounds, and pre-publish validation
│   └── integration/
│       ├── test_auth.py         # Full auth suite (register, login, refresh, logout)
│       ├── test_health.py       # Health & DB connectivity checks
│       ├── test_organizations.py# Multi-tenant isolation & member tests
│       ├── test_templates.py    # Template CRUD, version immutability, clone, archive
│       └── test_assets_and_preview.py # Image uploads, validation, font discovery, preview
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .env.example
├── .env
└── README.md
```

---

## 3. Quick Start & Local Setup

### Prerequisites
- Python 3.12+ (or 3.13)
- MongoDB running locally on `mongodb://localhost:27017` (e.g. Windows MongoDB Service)

### Installation
```bash
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env

# 4. Start local development server with auto-reload
uvicorn app.main:app --reload --port 8000
```

Interactive Swagger Documentation:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 4. Running Automated Tests

```bash
# Run the full test suite (45 tests)
pytest -v
```

All 45 test cases run against the isolated `certificate_platform_test` database and teardown automatically.

---

## 5. P1 Template Management Features

### Version Immutability
- Once a template version is **published**, it is strictly locked and immutable.
- Edits require creating a new draft version (e.g., `v2`). This guarantees historical certificate reproducibility.

### Placeholder Architecture
- Syntax: `{{variable_name}}`
- System fields automatically classified: `{{certificate_id}}`, `{{verification_code}}`, `{{verification_url}}`, `{{issued_at}}`.
- Recipient fields automatically extracted: `{{recipient_name}}`, `{{program_name}}`, `{{issue_date}}`, etc.
- Duplicate placeholders supported: 1 logical field, multiple visual positions.

### Asset Validation & Storage
- Assets (backgrounds, logos, signatures, seals) are validated by MIME type, magic bytes, and dimensions before storage.
- Stored on disk under `storage/assets/{org_id}/{template_id}/` outside MongoDB.

### High-Fidelity Preview
- `POST /api/v1/templates/{id}/preview` renders a PNG preview with sample data substitution, font rendering, and dynamic QR code generation.

---

## 6. P2 CSV / Excel Intelligence & Field Mapping

### Architecture & Pipeline

```text
Upload CSV/XLSX 
      ↓
File Validation & Security (MIME, size, macro .xlsm rejection)
      ↓
Delimiter & Encoding Sniffer (comma, semicolon, tab, pipe; UTF-8, UTF-8-SIG, Windows-1252)
      ↓
Header & Empty Row Filter
      ↓
Column Profiling & Data Type Detection (string, email, date, number, url)
      ↓
Deterministic Field Matching Pipeline:
  [Level 1: Exact] → [Level 2: Normalized] → [Level 3: Synonym Dictionary] → [Level 4: Data Type] → [Level 5: Fuzzy Levenshtein]
      ↓
Confidence Calculation (High: 90-100%, Medium: 70-89%, Low: <70%)
      ↓
Mapping Confirmation & Profile Persistence (`mapping_profiles`)
      ↓
Row-Level Data Cleaning & Validation (Email syntax, ISO YYYY-MM-DD date normalization, Long name >40 char warnings, Duplicate detection)
      ↓
Normalized Recipient Dataset (`import_rows`)
      ↓
Status: `ready` (Trusted bridge to Phase P3 Certificate Engine)
```

### MongoDB Collections Added in P2

| Collection | Key Fields | Indexes |
|---|---|---|
| `imports` | `organization_id`, `template_id`, `template_version_id`, `filename`, `status`, `total_rows`, `valid_rows`, `invalid_rows`, `warning_rows` | `organization_id` + `created_at`, `organization_id` + `status`, `organization_id` + `template_id` |
| `import_mappings` | `import_id`, `template_version_id`, `organization_id`, `mappings` (source_column, target_field, confidence, method) | `import_id`, `organization_id` + `template_version_id` |
| `import_rows` | `import_id`, `organization_id`, `row_number`, `data`, `status` (valid, warning, error), `errors`, `warnings` | `import_id` + `row_number`, `import_id` + `status` |
| `mapping_profiles` | `organization_id`, `template_id`, `name`, `mappings` | `organization_id` + `template_id`, `organization_id` + `name` |

### P2 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/imports` | Upload CSV/XLSX recipient file & trigger automated column profiling & auto-mapping |
| `GET` | `/api/v1/imports` | List imports with pagination and status/template filtering |
| `GET` | `/api/v1/imports/{id}` | Get detailed import status and summary |
| `GET` | `/api/v1/imports/{id}/progress` | Real-time import processing and validation progress |
| `GET` | `/api/v1/imports/{id}/mapping` | Retrieve auto-suggested or confirmed column-to-field mappings |
| `POST` | `/api/v1/imports/{id}/mapping` | Confirm column mapping and trigger full dataset validation |
| `POST` | `/api/v1/imports/{id}/validate` | Re-run dataset validation against confirmed mapping |
| `GET` | `/api/v1/imports/{id}/preview` | Preview top 20 recipient rows with validation status |
| `GET` | `/api/v1/imports/{id}/rows` | List paginated recipient records (filtered by `valid`, `warning`, `error`) |
| `GET` | `/api/v1/imports/{id}/errors` | Retrieve all validation failure rows with error codes & messages |
| `GET` | `/api/v1/imports/{id}/errors/download` | Download downloadable `errors.csv` report |
| `POST` | `/api/v1/imports/{id}/replace` | Re-upload fixed spreadsheet without re-creating import metadata |
| `POST` | `/api/v1/imports/{id}/cancel` | Cancel an ongoing or pending import job |
| `GET` | `/api/v1/mapping-profiles` | List saved organization mapping profiles |
| `POST` | `/api/v1/mapping-profiles` | Save reusable column mapping profile |
| `DELETE` | `/api/v1/mapping-profiles/{id}` | Delete mapping profile |

---

## 7. P3 — Certificate Rendering & Verification Engine

P3 provides high-fidelity canvas rendering, smart-fit auto font sizing, QR code stamping, PDF generation via ReportLab, SHA-256 fingerprinting, and public verification.

### P3 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/certificates/preview` | Render preview PNG without persisting certificate record |
| `POST` | `/api/v1/certificates/generate` | Official certificate issuance (idempotent, atomic sequence) |
| `GET` | `/api/v1/certificates` | List organization certificates with filtering |
| `GET` | `/api/v1/certificates/{id}` | Get certificate details and metadata |
| `GET` | `/api/v1/certificates/{id}/pdf` | Secure PDF download |
| `GET` | `/api/v1/certificates/{id}/preview` | Download certificate preview PNG |
| `POST` | `/api/v1/certificates/{id}/revoke` | Revoke certificate with reason |
| `GET` | `/api/v1/verify/{code}` | Public verification endpoint (no auth required) |

---

## 8. P4 — Bulk Certificate Issuance, Queue & Worker System

P4 scales issuance to 10,000+ recipients with asynchronous job queues, background workers, atomic claiming, crash recovery, and streaming ZIP downloads.

### Architecture

```text
User / Frontend
      ↓
POST /api/v1/issuance-jobs
      ↓
FastAPI (Creates job & items in MongoDB)
      ↓
Redis Queue (ARQ)
      ↓
Background Workers (ARQ)
  ├── Atomic claim item (findOneAndUpdate)
  ├── Idempotency check
  ├── P3 Certificate Engine
  ├── SHA-256 & Storage
  └── Progress updates
      ↓
Progress / ZIP Stream Export
```

### P4 Collections

| Collection | Key Fields | Indexes |
|---|---|---|
| `issuance_jobs` | `organization_id`, `template_id`, `template_version_id`, `import_id`, `status`, `total`, `pending`, `processing`, `completed`, `failed`, `cancelled`, `progress` | `organization_id` + `created_at`, `organization_id` + `status`, `import_id`, `template_id` |
| `issuance_job_items` | `job_id`, `organization_id`, `import_row_id`, `row_number`, `status`, `certificate_id`, `attempts`, `error`, `recipient`, `data` | `job_id` + `status`, `job_id` + `row_number`, `job_id` + `certificate_id`, `job_id` + `import_row_id` (unique) |

### P4 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/issuance-jobs` | Create and enqueue a bulk issuance job |
| `GET` | `/api/v1/issuance-jobs` | List organization issuance jobs |
| `GET` | `/api/v1/issuance-jobs/{id}` | Get details of an issuance job |
| `GET` | `/api/v1/issuance-jobs/{id}/progress` | Real-time progress and completion percentages |
| `POST` | `/api/v1/issuance-jobs/{id}/pause` | Pause job (workers stop claiming new items) |
| `POST` | `/api/v1/issuance-jobs/{id}/resume` | Resume paused job |
| `POST` | `/api/v1/issuance-jobs/{id}/cancel` | Cancel remaining items (keeps already generated certs) |
| `POST` | `/api/v1/issuance-jobs/{id}/retry-failed` | Re-queue all failed items |
| `POST` | `/api/v1/issuance-jobs/{id}/items/{item_id}/retry` | Retry a single failed item |
| `GET` | `/api/v1/issuance-jobs/{id}/items` | List paginated job items with filter by status or recipient |
| `GET` | `/api/v1/issuance-jobs/{id}/errors` | Retrieve failure error list |
| `GET` | `/api/v1/issuance-jobs/{id}/errors/download` | Download `issuance-errors.csv` report |
| `POST` | `/api/v1/issuance-jobs/{id}/zip` | Request asynchronous ZIP archive creation |
| `GET` | `/api/v1/issuance-jobs/{id}/zip` | Check ZIP generation status & expiry |
| `GET` | `/api/v1/issuance-jobs/{id}/zip/download` | Download generated certificates ZIP archive |

### Running Workers

```bash
# Start background worker process locally
arq app.workers.worker.WorkerSettings
```

---

## 9. P5 — Verification, QR, Certificate Lifecycle & Trust System

P5 provides the trust layer: public QR/URL verification, privacy protections, full revocation and restore lifecycle, cryptographic SHA-256 tamper detection, scan event tracking, and rate limiting.

### Verification Flow

```text
Certificate PDF / Printed Copy
              │
              ▼
           QR Code
              │
              ▼
   Public Verification URL
(https://certiflow.io/verify/{code})
              │
              ▼
       FastAPI Public API
              │
      ┌───────┴───────┐
      ▼               ▼
Redis Cache     MongoDB Lookup
 (300s TTL)    (Unique Index)
      │               │
      └───────┬───────┘
              ▼
      Privacy Filtering
  (No email, internal IDs, or keys)
              │
              ▼
   Public Verification Result
 (VALID / REVOKED / EXPIRED / INVALID)
```

### P5 API Endpoints

#### Public Endpoints (No Authentication Required)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/public/verify/{code}` | Verify certificate by public code (cached in Redis, rate-limited) |
| `POST` | `/api/v1/public/verify-file` | Verify original PDF file by cryptographic SHA-256 hash match |
| `GET` | `/api/v1/public/certificates/{code}/download` | Public certificate PDF download (if enabled by issuer) |

#### Authenticated Lifecycle & Trust Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/certificates/{id}/revoke` | Revoke certificate with structured reason, notes & cache invalidation |
| `POST` | `/api/v1/certificates/{id}/restore` | Restore revoked certificate to active status |
| `POST` | `/api/v1/certificates/bulk-revoke` | Bulk revoke multiple certificates by IDs |
| `GET` | `/api/v1/certificates/{id}/integrity` | Cryptographic SHA-256 integrity verification of stored PDF |
| `GET` | `/api/v1/certificates/{id}/timeline` | Complete audit and scan timeline of certificate lifecycle |
| `GET` | `/api/v1/certificates/{id}/verification-events` | List recorded public verification scan attempts |

---

## 10. Phase 6 — Email Delivery, Notifications & Certificate Distribution

Phase 6 implements a robust, asynchronous, multi-tenant email delivery system for automated and bulk certificate distribution.

### Core Architecture

```text
Certificate Generated (P3/P4)
              │
              ▼
   P6 Email Queue (Redis / ARQ)
              │
              ▼
        Email Worker
  ┌───────────┴───────────┐
  ▼                       ▼
Mock Provider       SMTP / API
  │                       │
  ▼                       ▼
Recipient           Recipient
  │                       │
  └───────────┬───────────┘
              ▼
      Provider Webhooks
  (delivered / bounced / complaint)
              │
              ▼
  Email Delivery Status & Timeline
```

### Key Capabilities

1. **Provider Abstraction**: Extensible interface (`EmailProvider`) supporting `MockEmailProvider` and `SMTPEmailProvider` (with STARTTLS and error code normalization).
2. **Organization Email Settings**: Per-tenant sender configuration, custom SMTP credentials (secrets never returned in API responses), and `auto_email_on_issuance` toggle.
3. **Template Engine & Variable Security**: Strict placeholder validation against allowed certificate/recipient/org variables (`{{recipient_name}}`, `{{certificate_number}}`, `{{verification_url}}`, `{{download_url}}`, etc.) with strict HTML-escaping to prevent XSS and template injection.
4. **Three Delivery Modes**:
   - `link`: HMAC-SHA256 signed temporary download URL.
   - `attachment`: Direct PDF attachment with size limit checks (`MAX_EMAIL_ATTACHMENT_SIZE_MB=10`) and filename sanitization.
   - `both`: Download link + PDF attachment.
5. **Bulk Email Jobs & Progress Tracking**: Separate asynchronous job coordinator (`email_jobs` + `email_deliveries`) supporting controlled worker concurrency, rate limiting, and progress metrics.
6. **Provider Webhooks & Idempotency**: Webhook endpoint (`/api/v1/webhooks/email/{provider}`) with signature verification, deduplication (`provider_event_id`), and lifecycle event tracking (`email_events`).
7. **Bounce & Complaint Handling**: Automatic addition of hard bounces and spam complaints to organization suppression list (`email_suppressions`), with pre-send suppression checks protecting sender reputation.

### P6 API Endpoints

#### Email Templates

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/email/templates` | Create reusable email template with variable validation |
| `GET` | `/api/v1/email/templates` | List organization email templates |
| `GET` | `/api/v1/email/templates/{id}` | Get email template details |
| `PUT` | `/api/v1/email/templates/{id}` | Update email template |
| `DELETE` | `/api/v1/email/templates/{id}` | Delete email template |

#### Settings, Preview & Suppression List

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/email/settings` | Get organization email settings (secrets masked) |
| `PUT` | `/api/v1/email/settings` | Update email provider settings (admin/owner only) |
| `POST` | `/api/v1/email/preview` | Preview email rendering with certificate context |
| `POST` | `/api/v1/email/test` | Send test email |
| `GET` | `/api/v1/email/suppressions` | List suppressed email addresses |
| `POST` | `/api/v1/email/suppressions` | Add email address to suppression list |
| `DELETE` | `/api/v1/email/suppressions/{email}` | Remove email from suppression list |

#### Certificate Email Issuance

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/certificates/{id}/email` | Queue certificate email delivery |
| `POST` | `/api/v1/certificates/{id}/resend-email` | Resend certificate email (preserves audit history) |

#### Bulk Email Jobs & Deliveries

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/email-jobs` | Create and start bulk email job |
| `GET` | `/api/v1/email-jobs` | List bulk email jobs with pagination |
| `GET` | `/api/v1/email-jobs/{id}` | Get bulk email job details |
| `GET` | `/api/v1/email-jobs/{id}/progress` | Real-time progress and delivery rate metrics |
| `POST` | `/api/v1/email-jobs/{id}/pause` | Pause email job |
| `POST` | `/api/v1/email-jobs/{id}/resume` | Resume paused email job |
| `POST` | `/api/v1/email-jobs/{id}/cancel` | Cancel email job |
| `GET` | `/api/v1/email-deliveries` | List deliveries with status/certificate filtering |
| `GET` | `/api/v1/email-deliveries/{id}` | Get delivery details with event audit timeline |
| `POST` | `/api/v1/email-deliveries/{id}/retry` | Retry failed email delivery |

#### Provider Webhooks

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/webhooks/email/{provider}` | Webhook for delivery, bounce, and complaint notifications |

---

## 11. P7 — Dashboard, Analytics, Reporting & Intelligence

P7 turns the platform into a multi-tenant SaaS control center. It computes precise KPIs, tracks comparative percentage changes, provides multi-field certificate search, unifies certificate audit/delivery/scan timelines, processes asynchronous background reports (CSV & ReportLab PDF), and handles pre-aggregated daily analytics.

### Analytics Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/analytics/dashboard` | Main organization dashboard with KPIs, deltas, trend chart, status distribution, recent jobs |
| `GET` | `/api/v1/analytics/certificates` | Certificate issuance trends, by template, by program, status counts |
| `GET` | `/api/v1/analytics/issuance` | Bulk issuance throughput (certs/min), average duration, failure classification |
| `GET` | `/api/v1/analytics/emails` | Email funnels, delivery rates (%), bounce rates (%), failure reason breakdown |
| `GET` | `/api/v1/analytics/verification` | Verification scan attempts, validity distribution, daily trends, top scanned certs |
| `GET` | `/api/v1/analytics/templates` | Template popularity, version distribution, last used timestamps |
| `GET` | `/api/v1/analytics/imports` | CSV/Excel import analytics, row counts, mapping quality metrics |
| `GET` | `/api/v1/analytics/usage` | Monthly certificate, email, and storage quotas |
| `GET` | `/api/v1/analytics/storage` | Disk storage consumption breakdown in MB (certificates, assets, reports) |
| `GET` | `/api/v1/analytics/health` | Operational health check for API, MongoDB, Redis, Storage, and Email (Owner/Admin) |

### Report Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/reports` | Create asynchronous background report job (CSV or ReportLab PDF) |
| `GET` | `/api/v1/reports` | List generated reports with pagination |
| `GET` | `/api/v1/reports/{id}` | Get report job status and signed download URL |
| `GET` | `/api/v1/reports/{id}/download` | Secure report download via signed HMAC token or session auth |

### Activity Feed & Advanced Search

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/activity` | Paginated organization activity and audit log feed |
| `GET` | `/api/v1/certificates` | Advanced certificate search by query, status, template, program, date range |
| `GET` | `/api/v1/certificates/{id}/timeline` | Complete unified lifecycle timeline combining generation, verification, and email webhooks |

---

## 12. Running Automated Tests

```bash
# Run pure unit tests (instant, 116 tests, no DB needed)
pytest -m no_db

# Run full integration test suite (65 tests against MongoDB)
pytest tests/integration/

# Run complete test suite (181 tests)
pytest
```

