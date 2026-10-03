# CertiFlow — Unified REST API Reference Specification

**API Base URL**: `http://127.0.0.1:8000` (Local Development) | `https://api.certiflow.io` (Production)  
**Standard Protocol**: HTTP/1.1 and HTTP/2 over TLS 1.3  
**Authentication**: Bearer JWT Token (`Authorization: Bearer <token>`) OR HttpOnly session cookie (`certiflow_access_token`)  
**API Envelope**: All responses adhere to the standard `APIResponse[T]` envelope:

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "request_id": "req_7f8e5721676b"
}
```

In the event of an error:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request payload or parameters",
    "details": [ ... ]
  },
  "request_id": "req_7f8e5721676b"
}
```

---

## 1. Complete Router Inventory (18 Domains)

| Domain | Base Path | Description | Security Level |
| :--- | :--- | :--- | :---: |
| **1. Authentication** | `/api/v1/auth` | User registration, login, token refresh, password resets, demo sessions | Public & Authenticated |
| **2. Organizations** | `/api/v1/organizations` | Tenant settings, organization metadata, tenant switching | Authenticated (Member+) |
| **3. Users** | `/api/v1/users` | Profile updates, password changes, notification preferences | Authenticated (Self) |
| **4. Templates** | `/api/v1/templates` | Certificate canvas designs, layer configurations, immutable versioning | Authenticated (Member+) |
| **5. Imports & Datasets** | `/api/v1/imports` | CSV/XLSX spreadsheet ingest, schema profiling, column mapping | Authenticated (Member+) |
| **6. Certificates** | `/api/v1/certificates` | Issued certificate registry, PDF binary downloads, revocations | Authenticated (Member+) |
| **7. Issuance Jobs** | `/api/v1/issuance-jobs` | Asynchronous ARQ worker batch generation, live progress, ZIP downloads | Authenticated (Admin+) |
| **8. Public Verification** | `/api/v1/public` | Public QR code verification, SHA-256 PDF integrity check | Public (Rate-Limited) |
| **9. Digital Credentials** | `/api/v1/credentials` | W3C Verifiable Credentials v2.0, Open Badges 3.0, Ed25519 key rotation | Authenticated (Admin+) |
| **10. Teams & RBAC** | `/api/v1/teams` | Multi-seat invitations, role assignments (Owner, Admin, Member, Viewer) | Authenticated (Admin+) |
| **11. API Keys** | `/api/v1/api-keys` | High-entropy developer keys (`ck_live_...`), scopes, key revocation | Authenticated (Admin+) |
| **12. Webhooks** | `/api/v1/webhooks` | Outbound HMAC-SHA256 event subscriptions, webhook test dispatches | Authenticated (Admin+) |
| **13. Audit Logs** | `/api/v1/audit-logs` | Immutable operational audit trail, security events, IP tracking | Authenticated (Admin+) |
| **14. Analytics** | `/api/v1/analytics` | Issuance KPIs, 30-day trends, verification rate calculations | Authenticated (Viewer+) |
| **15. Reports** | `/api/v1/reports` | Custom batch summaries and CSV compliance exports | Authenticated (Member+) |
| **16. Billing & Quotas** | `/api/v1/billing` | Subscription plans (Starter, Pro, Enterprise), Stripe billing portals | Authenticated (Owner only) |
| **17. Email Outbox** | `/api/v1/email` | Delivery tracking, outbox staging, resend throttling | Authenticated (Admin+) |
| **18. System & Health** | `/health`, `/api/v1/health` | Liveness, readiness probes, MongoDB & Redis heartbeat, Prometheus metrics | Public |

---

## 2. Endpoint Specifications by Router

### 2.1 Authentication (`/api/v1/auth`)

#### `POST /api/v1/auth/register`
Creates a new user account and provisions a default tenant organization atomically.
* **Payload**:
  ```json
  {
    "name": "Jane Doe",
    "email": "jane@company.com",
    "password": "SecurePassword2026!"
  }
  ```
* **Response (201 Created)**: Returns `TokenResponse` with `access_token`, `refresh_token`, `user`, and `organization`. Sets HttpOnly cookies.

#### `POST /api/v1/auth/login`
Authenticates user credentials against Argon2id password hash.
* **Payload**:
  ```json
  {
    "email": "jane@company.com",
    "password": "SecurePassword2026!"
  }
  ```
* **Response (200 OK)**: Returns `TokenResponse` and sets cookies.

#### `POST /api/v1/auth/refresh`
Rotates JWT access and refresh tokens. Invalidates the used refresh token (reuse detection).
* **Headers/Cookies**: Reads `certiflow_refresh_token` cookie or Bearer token.
* **Response (200 OK)**: Returns refreshed token pair.

#### `POST /api/v1/auth/logout`
Revokes active refresh token and clears HttpOnly session cookies.
* **Response (200 OK)**: `{"message": "Successfully logged out"}`.

#### `GET /api/v1/auth/me`
Retrieves authenticated user identity and active tenant organization profile.
* **Headers**: `Authorization: Bearer <access_token>`.
* **Response (200 OK)**: Returns user ID, email, name, role, and organization ID.

#### `POST /api/v1/auth/forgot-password`
Generates single-use password reset token with account enumeration defense. Always returns 200 OK.
* **Payload**: `{"email": "jane@company.com"}`.

#### `POST /api/v1/auth/reset-password`
Consumes reset token and re-hashes new password using Argon2id.
* **Payload**: `{"token": "secure_token_str", "password": "NewSecurePassword2026!"}`.

---

### 2.2 Templates (`/api/v1/templates`)

#### `GET /api/v1/templates`
Lists all certificate templates for the authenticated organization.
* **Query Params**: `page` (default 1), `limit` (default 20).
* **Response (200 OK)**: Paginated array of template metadata.

#### `POST /api/v1/templates`
Creates a new certificate template project.
* **Payload**:
  ```json
  {
    "name": "AI Workshop 2026 Diploma",
    "description": "Annual completion award",
    "canvas": {
      "width": 1920,
      "height": 1080,
      "background_color": "#ffffff"
    }
  }
  ```

#### `POST /api/v1/templates/{id}/versions`
Publishes an immutable snapshot of template layers for deterministic batch compilation.
* **Payload**:
  ```json
  {
    "layers": [
      {
        "id": "layer_01",
        "type": "text",
        "name": "Recipient Name",
        "content": "{{NAME}}",
        "x": 50.0,
        "y": 45.0,
        "font_size": 36,
        "font_family": "Playfair Display",
        "auto_fit": true
      }
    ]
  }
  ```
* **Response (201 Created)**: Returns published `template_version_id`.

---

### 2.3 Bulk Issuance Jobs (`/api/v1/issuance-jobs`)

#### `POST /api/v1/issuance-jobs`
Enqueues a bulk generation job to the Redis ARQ worker cluster.
* **Payload**:
  ```json
  {
    "template_version_id": "tpl_ver_6abf84814129",
    "recipients": [
      {
        "name": "Atul Kumar",
        "course": "Advanced Deep Learning",
        "email": "atul@example.com",
        "date": "Sep 28, 2026"
      }
    ],
    "idempotency_key": "job_batch_001_idemp"
  }
  ```
* **Response (202 Accepted)**: Returns `job_id`, initial status `PENDING`, and progress URL.

#### `GET /api/v1/issuance-jobs/{id}`
Polls real-time progress of batch generation.
* **Response (200 OK)**:
  ```json
  {
    "id": "job_6abf84814129",
    "status": "PROCESSING",
    "total_count": 500,
    "processed_count": 340,
    "failed_count": 0,
    "progress_percent": 68.0,
    "created_at": "2026-10-02T10:00:00Z"
  }
  ```

#### `GET /api/v1/issuance-jobs/{id}/download-zip`
Streams the compiled ZIP archive containing all signed PDFs.
* **Response (200 OK)**: `application/zip` streaming byte stream with `Content-Disposition: attachment`.

---

### 2.4 Public Verification (`/api/v1/public`)

#### `GET /api/v1/public/verify/{code}`
Public resolution of QR code verification link. Privacy-preserving (omits private contact details).
* **Response (200 OK)**:
  ```json
  {
    "valid": true,
    "status": "ISSUED",
    "certificate": {
      "id": "cert_6abf84814129",
      "certificate_number": "CERT-AF72K9",
      "recipient_name": "Atul Kumar",
      "course_name": "AI Workshop 2026",
      "issued_at": "2026-09-28T10:00:00Z",
      "issuer_name": "Acme Academy",
      "sha256_fingerprint": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
  }
  ```

#### `POST /api/v1/public/verify-file`
Multipart upload of physical certificate PDF to verify cryptographic integrity against the ledger.
* **Form Field**: `file` (`application/pdf`).
* **Response (200 OK)**: Returns calculated SHA-256 hash and matched certificate record.

#### `POST /api/v1/public/credentials/verify`
Cryptographically verifies third-party W3C Verifiable Credential JSON-LD with Ed25519 signature.
* **Payload**: W3C VC JSON object.
* **Response (200 OK)**: `{"verified": true, "issuer_did": "did:web:certiflow.io"}`.

---

### 2.5 System Health & Probes (`/health`)

#### `GET /health` & `GET /api/v1/health/ready`
Readiness probe verifying connectivity to MongoDB replica set and Redis queue.
* **Response (200 OK)**:
  ```json
  {
    "status": "ready",
    "database": "connected",
    "redis": "connected",
    "timestamp": "2026-10-02T10:16:33Z"
  }
  ```
