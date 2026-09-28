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

## 12. P8 — Teams, RBAC, API Keys, Developer API & Webhooks

P8 evolves CertiFlow from a single-organization application into a full multi-user, multi-tenant SaaS platform with programmatic developer integrations.

```text
                    ORGANIZATION
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
        Users          Teams       API Clients
          │              │              │
          └──────────────┼──────────────┘
                         ↓
                       RBAC
                         │
              ┌──────────┼──────────┐
              ↓          ↓          ↓
             UI         API       Webhooks
```

### Key Capabilities

1. **Multi-Organization & Switching**: Users can belong to multiple organizations with distinct roles. Active organization context is switchable via `POST /api/v1/organization/switch` or client-controlled `X-Organization-Id` header validated against server-side membership.
2. **Secure Invitations & Member Lifecycle**: Single-use cryptographically secure invitation tokens (SHA-256 hashed in database). Member suspension restricts operational actions while preserving historical audit logs. Sole organization owners cannot be deleted without prior explicit ownership transfer.
3. **Fine-Grained RBAC & Custom Roles**: Central permission registry (`PERMISSIONS`) with default system roles (`owner`, `admin`, `member`, `viewer`) and custom organization roles. Protected server-side via `require_permission(permission)`.
4. **Teams System**: Departmental groupings (`teams`, `team_members`) for organizing workforce and permissions.
5. **Developer API & API Keys**: High-entropy keys prefixed with `ck_live_` shown only once at creation time, securely hashed for storage. Granular scopes (`certificates:read`, `certificates:create`, etc.), sliding-window Redis rate limiting, request IDs, and request idempotency via `Idempotency-Key`.
6. **Service Accounts**: Non-human machine accounts for ERP/LMS integrations.
7. **Outbound Webhooks**: Event subscriptions for lifecycle triggers (`certificate.generated`, `certificate.revoked`, `certificate.restored`, `issuance_job.completed`, `email.sent`, `email.delivered`, `email.bounced`). Signed with HMAC-SHA256 (`X-Webhook-Signature`, `X-Webhook-Timestamp`), replay attack prevention, strict SSRF protection blocking loopback and cloud metadata IPs, and background ARQ worker delivery with exponential retry backoff.
8. **API Usage Telemetry**: Latency tracking, status code distribution (2xx, 4xx, 5xx, 429), and top endpoint breakdown via `GET /api/v1/api-usage`.

### P8 API Endpoints

| Category | Method | Endpoint | Description |
|---|---|---|---|
| **Members** | `GET` | `/api/v1/organization/members` | List members with status filtering & pagination |
| | `PATCH` | `/api/v1/organization/members/{id}` | Update member role or suspension status |
| | `DELETE` | `/api/v1/organization/members/{id}` | Remove member (soft removal preserving audit logs) |
| | `POST` | `/api/v1/organization/transfer-ownership` | Transfer organization ownership to an active member |
| | `POST` | `/api/v1/organization/switch` | Switch active organization and issue scoped session tokens |
| **Invitations** | `POST` | `/api/v1/organization/invitations` | Invite a member by email with specified role |
| | `GET` | `/api/v1/organization/invitations` | List pending and historical organization invitations |
| | `POST` | `/api/v1/organization/invitations/{id}/resend` | Refresh and resend an invitation token |
| | `DELETE` | `/api/v1/organization/invitations/{id}` | Cancel/revoke a pending invitation |
| | `POST` | `/api/v1/organization/invitations/accept` | Accept an invitation token & join organization |
| **Roles** | `GET` | `/api/v1/roles` | List system and custom roles |
| | `POST` | `/api/v1/roles` | Create a custom role with defined permissions |
| | `GET` | `/api/v1/roles/{id}` | Get details of a system or custom role |
| | `PATCH` | `/api/v1/roles/{id}` | Update custom role name, description, or permissions |
| | `DELETE` | `/api/v1/roles/{id}` | Delete custom role (blocked if members are assigned) |
| | `GET` | `/api/v1/roles/permissions/registry` | List all valid permissions in the platform registry |
| **Teams** | `GET` | `/api/v1/teams` | List organization teams |
| | `POST` | `/api/v1/teams` | Create a new team |
| | `GET` | `/api/v1/teams/{id}` | Get team details |
| | `PATCH` | `/api/v1/teams/{id}` | Update team name or description |
| | `DELETE` | `/api/v1/teams/{id}` | Delete a team |
| | `GET` | `/api/v1/teams/{id}/members` | List members of a team |
| | `POST` | `/api/v1/teams/{id}/members` | Add an active organization member to a team |
| | `DELETE` | `/api/v1/teams/{id}/members/{user_id}` | Remove a member from a team |
| **API Keys** | `GET` | `/api/v1/api-keys` | List organization API keys (secrets omitted) |
| | `POST` | `/api/v1/api-keys` | Generate high-entropy API key (returned plaintext once) |
| | `GET` | `/api/v1/api-keys/{id}` | Get API key metadata |
| | `POST` | `/api/v1/api-keys/{id}/revoke` | Revoke an API key immediately |
| | `DELETE` | `/api/v1/api-keys/{id}` | Delete API key record |
| **Service Accounts** | `GET` | `/api/v1/service-accounts` | List service accounts |
| | `POST` | `/api/v1/service-accounts` | Create a service account for machine integrations |
| | `GET` | `/api/v1/service-accounts/{id}` | Get service account details |
| | `PATCH` | `/api/v1/service-accounts/{id}` | Update service account details |
| | `DELETE` | `/api/v1/service-accounts/{id}` | Delete a service account |
| **Outbound Webhooks** | `GET` | `/api/v1/webhooks` | List webhook subscriptions |
| | `POST` | `/api/v1/webhooks` | Register webhook subscription with event filters |
| | `GET` | `/api/v1/webhooks/{id}` | Get webhook endpoint details |
| | `PATCH` | `/api/v1/webhooks/{id}` | Update URL, events, or status |
| | `DELETE` | `/api/v1/webhooks/{id}` | Delete webhook endpoint |
| | `POST` | `/api/v1/webhooks/{id}/test` | Send test webhook ping & verify connectivity |
| | `POST` | `/api/v1/webhooks/{id}/rotate-secret` | Rotate HMAC signing secret |
| | `GET` | `/api/v1/webhooks/{id}/deliveries` | List delivery history and response times |
| | `POST` | `/api/v1/webhook-deliveries/{id}/retry` | Manually retry a failed delivery |
| **API Usage** | `GET` | `/api/v1/api-usage` | Telemetry metrics (requests, 2xx, 4xx, 5xx, latency) |

---

## 13. Phase 9 — Security, Performance & Production Hardening (P9)

P9 elevates CertiFlow from a functional multi-tenant application to a battle-tested, production-hardened SaaS platform capable of surviving real-world attacks, high-load workloads, worker failures, and operational incidents.

### 13.1 Security Threat Model & Protections

| Attack Vector | Threat | Applied P9 Production Defense |
|---|---|---|
| **Credential Attacks** | Brute force login | IP + account rate limiting with progressive controls |
| **Account Enumeration** | Timing & response side-channel | Generic timing-safe forgot-password responses |
| **Password Reset** | Token prediction & replay | 32-byte cryptographically secure token, SHA-256 hash storage, 15-min TTL, single-use, revokes all sessions upon reset |
| **High-Risk Actions** | Session hijacking / CSRF | Re-authentication enforced via `X-Confirm-Password` header |
| **Cross-Tenant Access** | BOLA / IDOR violations | Strict organization scope filtering on every query + automated isolation matrix tests |
| **Malicious Uploads** | Executable masquerading | Real magic bytes signature validation for PNG, JPEG, PDF, XLSX, Fonts, and CSV |
| **SVG Injections** | XSS / XXE / Foreign objects | Rejection of `<script>` & `<!ENTITY>`, stripping of `onload`, `onclick`, `javascript:`, `<iframe>`, `<foreignObject>` |
| **Archive Exploits** | Zip Slip / Zip Bomb | Rejection of `..`, drive letters, path traversal; compression ratio limit (<100:1) and total extract limit (100MB) |
| **SSRF** | Internal network traversal | Resolution validation rejecting private RFC1918, loopback, link-local, and cloud metadata (169.254.169.254) |
| **NoSQL Injection** | Arbitrary MongoDB operators | Recursive `NoSQLSanitizer` stripping/rejecting `$` keys (`$where`, `$regex`, `$gt`, etc.) |
| **Clickjacking & Sniffing** | Browser vulnerabilities | Security headers middleware (`nosniff`, `DENY`, `strict-origin`, `Permissions-Policy`, `CSP`, `HSTS`) |

### 13.2 Reliability, Observability & Worker Recovery

- **Liveness & Readiness Probes**:
  - `GET /health`: Fast process liveness probe.
  - `GET /health/ready`: Validates live connectivity to MongoDB, Redis ARQ pool, and persistent storage write accessibility (returns HTTP 503 if critical dependency is degraded).
- **Prometheus Metrics**:
  - `GET /metrics`: Native in-memory Prometheus-compatible exporter publishing `certiflow_http_requests_total`, `certiflow_http_errors_total`, `certiflow_certificates_total`, `certiflow_emails_total`, and `certiflow_verifications_total`.
- **Worker Heartbeats & Recovery**:
  - Workers update `worker_heartbeats` collection periodically with status, worker ID, and timestamp.
  - `RecoveryService.recover_stuck_jobs`: Detects background tasks stuck in `processing` exceeding the timeout threshold, automatically retries transient failures, and routes persistently failed jobs to dead-letter status.
- **Production Version & Build Info**:
  - `GET /api/v1/version` and `GET /api/v1/build` for deployment tracking without exposing secrets.

### 13.3 P9 Production Endpoints Summary

| Category | Method | Endpoint | Description |
|---|---|---|---|
| **Auth Hardening** | `POST` | `/api/v1/auth/forgot-password` | Request password reset token (account-enumeration protected) |
| | `POST` | `/api/v1/auth/reset-password` | Reset password using single-use token; invalidates active sessions |
| **Diagnostics** | `GET` | `/health` | Root process liveness check |
| | `GET` | `/health/ready` | Orchestrator readiness probe (checks MongoDB, Redis, Storage) |
| | `GET` | `/api/v1/version` | Application version & commit identifier |
| | `GET` | `/api/v1/build` | Service environment & build metadata |
| **Observability** | `GET` | `/metrics` | Prometheus metrics exporter |

---

## 15. Phase 10 — Production Deployment, SaaS Infrastructure, Metering & Billing (P10)

P10 transforms CertiFlow from production-hardened software into a commercial, highly scalable, multi-tenant SaaS platform with end-to-end billing, subscription management, usage metering, quota enforcement, cost controls, admin operations, and CI/CD pipelines.

### 15.1 Decoupled Architecture

CertiFlow follows a strict decoupled architecture: **Plan → Subscription → Entitlement → Usage → Quota**. Billing logic is never mixed directly into certificate generation or worker routines.

```text
User / Org Action
      ↓
EntitlementService.can_access_feature() / get_limit()
      ↓
QuotaService.check_certificate_quota()
      ↓
CertificateService.generate() / Worker Pipeline
      ↓
UsageService.record_usage()
      ↓
[usage_counters] (Atomic $inc in YYYY-MM) + [usage_events] (Immutable Audit Log)
```

### 15.2 Plan Catalog & Entitlement Matrix

| Feature / Limit | Free Community | Starter | Professional | Business | Enterprise |
|---|---|---|---|---|---|
| **Monthly Price (INR)** | ₹0 | ₹499 | ₹1,999 | ₹7,999 | Custom |
| **Certificates / Mo** | 100 | 1,000 | 5,000 | 25,000 | 100,000+ |
| **Asset Storage** | 1 GB | 5 GB | 25 GB | 100 GB | 1 TB |
| **Templates** | 3 | 10 | 50 | 200 | 1,000 |
| **Team Seats** | 2 | 5 | 15 | 50 | 500 |
| **Developer REST API** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Outbound Webhooks** | ❌ | 2 | 10 | 50 | 200 |
| **Custom RBAC Roles** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Priority Queue** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **White-Label Email** | ❌ | ❌ | ✅ | ✅ | ✅ |

### 15.3 Subscription Lifecycle & Webhook Idempotency

- **Default Trial**: Every newly registered organization receives an automatic 14-day trial of the **Starter** plan.
- **Statuses**: `trialing` → `active` → `past_due` (with a 7-day grace period where generated certificates remain accessible) → `cancelled` / `expired`.
- **Safe Downgrades**: Downgrading to a lower plan preserves all historical templates and certificates while blocking new creation beyond the lower tier's quota.
- **Webhook Replay Protection**: Inbound webhooks (`POST /api/v1/billing/webhooks/{provider}`) use HMAC SHA-256 signature verification and enforce idempotency through a unique MongoDB index on `(provider, event_id)`. Re-delivering the same event is safe and produces no duplicate invoices or side effects.

### 15.4 Usage Metering & Quota Warning System

- **Atomic Increments**: Monthly counters are updated atomically via MongoDB `$inc` on `usage_counters` keyed by `(organization_id, metric, period)`.
- **Soft Warnings & Hard Limits**:
  - `80%` quota: Warning flag set on dashboard.
  - `90%` quota: Critical warning banner triggered.
  - `100%` quota: Hard limit reached; operations blocked with HTTP `403 Forbidden` (`CERTIFICATE_QUOTA_EXCEEDED`).
- **Promotional Overrides**: Platform admins can grant temporary or promotional quota additions (e.g. +10,000 certificates for 30 days) with automatic expiration tracking.

### 15.5 Infrastructure & CI/CD Artifacts

- **Multi-Stage Dockerfiles**:
  - `Dockerfile.api`: Production FastAPI image with unprivileged `appuser`, font dependencies, and curl health check.
  - `Dockerfile.worker`: Background ARQ worker container with ReportLab/Pillow fonts, graceful `SIGTERM` stop signal handling, and high-concurrency settings.
- **Docker Compose Orchestration**:
  - `docker-compose.prod.yml`: Multi-replica API and worker cluster with resource limits, Redis persistence (AOF), healthcheck policies, and container network isolation.
- **GitHub Actions CI/CD Pipeline**:
  - `.github/workflows/ci.yml`: Automated backend linting (flake8), comprehensive pytest suite with coverage against live MongoDB/Redis service containers, Docker image build validation, and Next.js frontend builds.
- **Operational Runbooks**:
  - `docs/runbooks/api-outage.md`: API triage, container diagnostics, and rolling zero-downtime restarts.
  - `docs/runbooks/billing-outage.md`: Inbound webhook desynchronization, HMAC troubleshooting, and grace period handling.
  - `docs/runbooks/disaster-recovery.md`: RPO $\le 1$h / RTO $\le 4$h database backup restoration and worker re-queueing procedures.
  - `docs/runbooks/worker-failure.md`: Queue backpressure, stalled job item recovery, and horizontal autoscaling.

### 15.6 P10 Production Endpoints Summary

| Category | Method | Endpoint | Description |
|---|---|---|---|
| **Plans** | `GET` | `/api/v1/plans` | Public catalog of active plans and full entitlement matrices |
| | `GET` | `/api/v1/plans/{plan_id}` | Detailed plan features and limits |
| **Subscriptions** | `GET` | `/api/v1/subscription` | Current organization subscription, status, and trial timeline |
| | `POST` | `/api/v1/subscription/checkout` | Create checkout session for plan upgrade or renewal |
| | `POST` | `/api/v1/subscription/cancel` | Schedule subscription cancellation at period end |
| | `POST` | `/api/v1/subscription/resume` | Resume active subscription scheduled for cancellation |
| **Billing & Usage** | `GET` | `/api/v1/billing/usage` | Monthly usage progress meters, percent used, and warning levels |
| | `GET` | `/api/v1/billing/invoices` | List payment invoices and receipts |
| | `GET` | `/api/v1/billing/invoices/{id}` | Retrieve individual invoice receipt details |
| | `GET` | `/api/v1/billing/cost-estimate` | Internal unit cost estimate and infrastructure breakdown |
| | `POST` | `/api/v1/billing/webhooks/{provider}` | Inbound webhook receiver with HMAC verification & idempotency |
| **SaaS Admin** | `GET` | `/api/v1/admin/overview` | Platform-wide KPIs, MRR calculation, and subscription stats |
| | `POST` | `/api/v1/admin/organizations/{id}/subscription` | Manually override subscription tier or status (Support) |
| | `POST` | `/api/v1/admin/organizations/{id}/entitlements/grant` | Grant temporary or promotional quota override |
| | `POST` | `/api/v1/admin/organizations/{id}/suspend` | Suspend organization for abuse or non-payment |
| | `POST` | `/api/v1/admin/organizations/{id}/restore` | Restore suspended organization to active standing |

---

## 17. P11 — Open Badges 3.0 + W3C Verifiable Credentials + Digital Credential Ecosystem

P11 elevates CertiFlow from a certificate generator into a **standards-compliant, portable digital credential platform**. It builds a machine-readable credential layer directly on top of the existing certificate infrastructure without replacing or disrupting human-readable PDF artifacts.

```text
                         Certificate SaaS
                               │
             ┌─────────────────┴─────────────────┐
             │                                   │
             ▼                                   ▼
      PDF Certificate                    Digital Credential
             │                                   │
             │                         ┌─────────┴─────────┐
             │                         │                   │
             ▼                         ▼                   ▼
       QR Verification          Open Badges 3.0      W3C VC v2.0
                                                         │
                                                         ▼
                                                  Cryptographic
                                                    Signature (Ed25519)
                                                         │
                                                         ▼
                                                   Credential
                                                     Status
                                                         │
                                      ┌──────────────────┼───────────────┐
                                      │                  │               │
                                      ▼                  ▼               ▼
                                  Verification        Wallet          Sharing
```

### 17.1 Core Standards & Data Models

1. **Decoupled Architecture**:
   - **Issuer Profile (`issuer_profiles`)**: Legal entity issuing credentials with stable public URLs and key discovery endpoints.
   - **Achievement Model (`achievements`)**: Defines the accomplishment ("What was achieved?") independently of any recipient.
   - **Credential Entity (`credentials`)**: Anchors the proof of accomplishment to a recipient with an opaque identifier (`cred_...`).
   - **Status Registry (`credential_status`)**: Real-time revocation and suspension list entry for instant third-party validation.
2. **Cryptographic Integrity**:
   - **Algorithm**: Asymmetric Ed25519 digital signatures.
   - **Canonicalization**: Deterministic RFC 8785 JSON canonicalization omitting detached `proof` block for cross-platform reproducibility.
   - **Proof Format**: W3C Data Integrity `Ed25519Signature2020`.
   - **Security at Rest**: Issuer private keys are encrypted at rest with Fernet (`settings.ENCRYPTION_KEY`). Never stored in plaintext.
   - **Key Rotation**: Active keys can be rotated without invalidating historical credentials; retired public keys remain queryable in `credential_keys`.
3. **Dual Standard Formats**:
   - **Open Badges 3.0**: 1EdTech / IMS Global JSON-LD (`OpenBadgeCredential`, `AchievementSubject`, `Criteria`, `Evidence`).
   - **W3C Verifiable Credentials v2.0**: W3C Recommendation (`VerifiableCredential`, `CertificationCredential`, `credentialStatus`).
4. **Privacy-by-Default**:
   - Public credential views reveal recipient display name and achievement criteria while strictly concealing recipient email addresses, phone numbers, and MongoDB internal IDs.
5. **Lifecycle Synchronization**:
   - Revoking a certificate in CertiFlow automatically synchronizes revocation to the digital credential and dedicated status registry.

### 17.2 P11 Credential Endpoints Summary

| Category | Method | Endpoint | Description |
|---|---|---|---|
| **Issuers** | `GET` | `/api/v1/issuers/profile` | Retrieve organization issuer profile and active key |
| | `PUT` | `/api/v1/issuers/profile` | Update issuer legal name, website, and public metadata |
| | `POST` | `/api/v1/issuers/keys/rotate` | Provision new active Ed25519 key while retiring prior key |
| **Achievements** | `POST` | `/api/v1/achievements` | Create achievement with skills, category, and criteria |
| | `GET` | `/api/v1/achievements` | List achievements defined by organization |
| | `GET` | `/api/v1/achievements/{id}` | Retrieve individual achievement definition |
| | `PUT` | `/api/v1/achievements/{id}` | Update achievement criteria, level, or skills |
| | `DELETE` | `/api/v1/achievements/{id}` | Delete achievement definition |
| **Credentials** | `POST` | `/api/v1/credentials` | Issue & sign digital credential for a certificate |
| | `GET` | `/api/v1/credentials` | List organization issued digital credentials |
| | `GET` | `/api/v1/credentials/{id}` | Detailed credential view with signature proof |
| | `POST` | `/api/v1/credentials/{id}/revoke` | Revoke digital credential with audit reason |
| | `POST` | `/api/v1/credentials/{id}/suspend` | Suspend credential temporarily |
| | `POST` | `/api/v1/credentials/{id}/restore` | Restore suspended credential to active standing |
| **Public Resolution** | `GET` | `/api/v1/public/issuers/{issuer_id}` | Public issuer profile and active/retired public keys |
| | `GET` | `/api/v1/public/credentials/{credential_id}` | Privacy-safe public credential presentation |
| | `GET` | `/api/v1/public/credentials/{credential_id}/verify` | Real-time signature, status, and expiration validation |
| | `GET` | `/api/v1/public/credentials/{credential_id}/badge` | 1EdTech Open Badges 3.0 JSON-LD document |
| | `GET` | `/api/v1/public/credentials/{credential_id}/vc` | W3C Verifiable Credentials Data Model v2.0 JSON |
| | `GET` | `/api/v1/public/credentials/{credential_id}/status` | Public credential status list entry |
| | `POST` | `/api/v1/public/credentials/verify` | Independent verifier for external W3C VC or Open Badge payloads |

---

## 18. Running Automated Tests

```bash
# Run pure unit tests (instant, no DB needed)
.venv\Scripts\pytest -m no_db

# Run digital credentials, cryptography, and standards test suites
.venv\Scripts\pytest tests/unit/test_credentials_and_cryptography.py tests/integration/test_credentials_and_issuance.py tests/security/test_credential_security.py

# Run Grand End-to-End P0-P11 Continuous Journey
.venv\Scripts\pytest tests/integration/test_full_e2e_p0_to_p11.py -v

# Run complete platform test suite (247 tests passing, 0 regressions)
.venv\Scripts\pytest
```




