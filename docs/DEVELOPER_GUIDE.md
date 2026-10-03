# CertiFlow — Comprehensive Developer & Contributor Guide

Welcome to the CertiFlow developer guide. This document provides an exhaustive, step-by-step walkthrough for configuring, developing, testing, debugging, and deploying the complete CertiFlow platform.

---

## 1. System Requirements & Prerequisites

CertiFlow consists of a **FastAPI (Python 3.12+)** backend microservice and a **Next.js 16 (React 19, TypeScript)** frontend application, backed by **MongoDB 7.0+** and **Redis 7.0+**.

### Required Runtimes & Tools

| Component | Minimum Version | Recommended | Purpose |
| :--- | :--- | :--- | :--- |
| **Node.js** | `v20.10.0 LTS` | `v22.x LTS` | Frontend runtime & Next.js Turbopack compiler |
| **npm** | `v10.0.0` | `v10.8+` | Frontend package manager |
| **Python** | `3.11.x` | `3.12.x` or `3.13.x` | Backend runtime & asynchronous worker processes |
| **MongoDB** | `7.0.x Community` | `7.0.x+` | Document store for organizations, certificates & templates |
| **Redis** | `7.0.x` | `7.2.x+` | In-memory cache & ARQ asynchronous task queue |
| **Git** | `2.40.x` | `Latest` | Version control |
| **Docker** | `24.0.x` (optional) | `Latest` | Multi-container local orchestration & production builds |

---

## 2. Repository Layout & Port Allocation

CertiFlow is structured as a unified monorepo:

```text
Certificate/
├── app/                  # Next.js 16 Turbopack Web Application (Frontend)
├── src/                  # Next.js Application Source Code (App Router, Zustand stores)
│   ├── app/              # App router routes ((auth), (marketing), app, verify)
│   ├── components/       # Marketing, UI, and Navigation component hierarchy
│   ├── features/         # Visual Editor Canvas, stores, and geometry engine
│   └── lib/              # API Client (dual auth), CSV engine, crypto verifier
├── Backend/              # FastAPI Application (Backend Microservice)
│   ├── app/              # FastAPI core, 18 REST routers, models, schemas, services
│   ├── tests/            # Pytest test suite (247 passing tests: unit, integration, security)
│   └── storage/          # Local asset and rendered artifact storage
├── docs/                 # Enterprise documentation suite
│   ├── ARCHITECTURE.md   # Architectural specification & separation of authority
│   ├── API_REFERENCE.md  # Complete 18-router REST API catalog
│   ├── DEVELOPER_GUIDE.md# (This file) Complete setup, configuration & test manual
│   ├── STANDARDS_COMPLIANCE.md # W3C VC v2.0, Open Badges 3.0 & Cryptography
│   └── USER_AND_PRODUCT_MANUAL.md # End-user, administrator & operator handbook
├── tests/                # Playwright End-to-End Test Suite (114 passing tests)
│   └── e2e/              # Golden path, auth, visual studio, CSV ingest, mobile suites
└── docker-compose.yml    # Full-stack multi-container composition
```

### Local Port Allocation Table

| Service | Host Port | Protocol | Notes |
| :--- | :--- | :--- | :--- |
| **Frontend (Next.js)** | `3000` | HTTP/1.1 & HTTP/2 | `http://localhost:3000` (Turbopack) |
| **Backend (FastAPI)** | `8000` | HTTP/1.1 (ASGI) | `http://127.0.0.1:8000` (Interactive docs at `/docs`) |
| **MongoDB Database** | `27017` | MongoDB Wire | Local Windows service or Docker container |
| **Redis Queue & Cache** | `6379` | RESP (Redis) | Local daemon or Docker container |

---

## 3. Step-by-Step Local Development Setup

### 3.1 Clone & Initialize

```powershell
# Windows PowerShell
git clone https://github.com/atul87/CertiFlow.git
cd CertiFlow
```

```bash
# macOS / Linux
git clone https://github.com/atul87/CertiFlow.git
cd CertiFlow
```

---

### 3.2 Database Setup (MongoDB & Redis)

#### Option A: Local Native Services (Windows)
1. **MongoDB**: Install MongoDB 7.0 Community Edition and verify the Windows Service is running:
   ```powershell
   Get-Service -Name MongoDB
   # If stopped:
   Start-Service -Name MongoDB
   ```
2. **Redis**: Run Redis on Windows via WSL2 or native port (e.g. Memurai or Redis for Windows):
   ```powershell
   # Test Redis connectivity
   redis-cli ping
   # Expected output: PONG
   ```

#### Option B: Docker for Databases Only
If you prefer running only databases in Docker while developing on bare metal:
```bash
docker run -d --name certiflow-mongo -p 27017:27017 -v mongo_data:/data/db mongo:7.0
docker run -d --name certiflow-redis -p 6379:6379 redis:7.2-alpine
```

---

### 3.3 Backend Setup (FastAPI)

1. **Navigate to the Backend directory and create a virtual environment**:
   ```powershell
   # Windows PowerShell
   cd e:\Certificate\Backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   ```bash
   # macOS / Linux
   cd Backend
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Python dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Install Playwright system dependencies (required for high-DPI PDF generation)**:
   ```bash
   playwright install chromium
   ```

4. **Configure Environment Variables**:
   Copy `.env.example` to `.env` in the `Backend/` directory:
   ```powershell
   # Windows
   Copy-Item .env.example .env
   ```
   ```bash
   # Linux / macOS
   cp .env.example .env
   ```
   *(See [Section 4: Environment Variables Reference](#4-environment-variables-reference) for required keys).*

5. **Start the FastAPI Development Server**:
   ```powershell
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   Verify backend health at: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) or explore Swagger UI at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

6. **Start the Background Task Worker (ARQ)** *(in a separate terminal)*:
   ```powershell
   # Windows PowerShell (with venv activated)
   cd e:\Certificate\Backend
   .\.venv\Scripts\Activate.ps1
   arq app.queue.worker.WorkerSettings
   ```

---

### 3.4 Frontend Setup (Next.js 16)

1. **Navigate to the project root and install Node dependencies**:
   ```bash
   cd e:\Certificate
   npm install
   ```

2. **Configure Frontend Environment Variables**:
   Create a `.env.local` file at the root directory:
   ```env
   NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
   NEXT_PUBLIC_APP_URL=http://localhost:3000
   ```

3. **Start the Next.js Turbopack Development Server**:
   ```bash
   npm run dev
   ```
   The application is accessible at [http://localhost:3000](http://localhost:3000).

---

## 4. Environment Variables Reference

### Backend Configuration (`Backend/.env`)

| Variable | Description | Security Level | Default Value | Notes |
| :--- | :--- | :---: | :--- | :--- |
| `ENVIRONMENT` | Deployment environment | Config | `development` | Set to `production` in live deployments |
| `DEBUG` | Enable verbose debugging | Config | `true` | Must be `false` in production |
| `PORT` | API server listen port | Config | `8000` | Port 8000 standard |
| `MONGODB_URL` | MongoDB connection URI | **Secret** | `mongodb://localhost:27017` | Include auth credentials in production |
| `DATABASE_NAME` | Active MongoDB database name | Config | `certiflow_dev` | Isolated per environment |
| `REDIS_URL` | Redis connection URI | **Secret** | `redis://localhost:6379/0` | Used for ARQ queue & rate limits |
| `JWT_SECRET_KEY` | Symmetric key for signing JWTs | **Critical** | *(Must be 32+ random hex)* | Never commit to Git |
| `JWT_ALGORITHM` | JWT signing algorithm | Security | `HS256` | Standard HMAC-SHA256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifespan | Security | `60` | 1 hour standard |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifespan | Security | `30` | 30 days standard |
| `FERNET_MASTER_KEY` | Master encryption key for Ed25519 private keys | **Critical** | *(32-byte urlsafe base64)* | Used to encrypt private keys at rest |
| `CORS_ORIGINS` | Permitted cross-origin hosts | Security | `http://localhost:3000,http://127.0.0.1:3000` | Comma-delimited list |
| `COOKIE_SECURE` | Enforce HTTPS for cookies | Security | `false` | Set to `true` in production |
| `COOKIE_DOMAIN` | Domain scope for session cookies | Security | `localhost` | Set to top-level domain in production |
| `STORAGE_BACKEND` | Asset storage backend | Config | `local` | `local` or `s3` |
| `STORAGE_LOCAL_DIR` | Local storage directory path | Config | `./storage` | Relative or absolute path |
| `EMAIL_PROVIDER` | Transactional email provider | Config | `mock` | `mock`, `smtp`, `sendgrid`, or `ses` |
| `SMTP_HOST` | Outgoing SMTP server address | Config | `smtp.mailtrap.io` | Required if `EMAIL_PROVIDER=smtp` |
| `SMTP_PORT` | Outgoing SMTP server port | Config | `587` | Port 587 (STARTTLS) or 465 (SSL) |
| `SMTP_USER` | SMTP username | **Secret** | `""` | Provided by email service |
| `SMTP_PASSWORD` | SMTP password | **Secret** | `""` | Provided by email service |
| `EMAILS_FROM_EMAIL` | Outgoing sender email address | Config | `noreply@certiflow.io` | Must be a verified sender domain |
| `STRIPE_API_KEY` | Stripe secret key for billing | **Critical** | `sk_test_...` | Required for subscription features |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signature secret | **Critical** | `whsec_...` | Prevents webhook spoofing |

---

## 5. Automated Testing Suite

CertiFlow maintains **100% passing automated test suites** across both backend and frontend.

### 5.1 Backend Pytest Suite (247 Tests)

The backend test suite is located in `Backend/tests/` and uses `pytest-asyncio` with an isolated in-memory or ephemeral test database.

```powershell
# Run the complete backend test suite
cd e:\Certificate\Backend
.\.venv\Scripts\Activate.ps1
pytest tests -v

# Run only unit tests (fast, in-memory)
pytest tests/unit -v

# Run integration tests (requires MongoDB)
pytest tests/integration -v

# Run security & cryptographic verification tests
pytest tests/security -v

# Run with test coverage report
pytest --cov=app --cov-report=term-missing
```

---

### 5.2 Frontend Playwright E2E Suite (114 Tests)

The end-to-end test harness runs against live Next.js and FastAPI instances, testing complete multi-browser and mobile user flows.

```bash
# Ensure both servers are running:
# 1. FastAPI on http://127.0.0.1:8000
# 2. Next.js on http://localhost:3000

# Run all Playwright tests across Chromium, Firefox, WebKit, and Mobile
npm run test:e2e

# Run only dedicated authentication E2E tests
npx playwright test tests/e2e/auth-system.spec.ts --project=chromium

# Run tests with interactive Playwright UI mode
npx playwright test --ui

# View HTML test execution report
npx playwright show-report
```

---

### 5.3 Static Analysis & Quality Assurance

```bash
# 1. TypeScript compilation check (Zero errors allowed)
npm run typecheck

# 2. ESLint code style and Next.js rule verification
npm run lint

# 3. Production build test (validates Turbopack bundling)
npm run build
```

---

## 6. Key Architectural Gotchas & Developer Rules

When contributing code to CertiFlow, you must adhere to the following architectural conventions:

### 1. Dual-Authentication (Bearer Token + HttpOnly Cookies)
In local development, the frontend runs on port `3000` while the backend runs on port `8000`. Browsers enforce strict cross-origin cookie policies.
- The frontend client (`src/lib/api/client.ts`) attaches both `credentials: 'include'` (for HttpOnly session cookies) and an `Authorization: Bearer <token>` header stored in `tokenStorage`.
- The active organization ID is automatically attached via the `X-Organization-Id` header.
- Always retrieve and persist tokens via `src/lib/api/auth.ts` helpers.

### 2. RFC 6761 Reserved TLDs in Email Validation
Pydantic v2 uses `email-validator`, which strictly blocks RFC 6761 reserved TLDs (such as `.test`, `.example`, `.invalid`).
- **Never** use emails like `user@certiflow.test` in test fixtures or seed scripts.
- **Always** use valid domain names such as `user@certiflow.io` or `user@example.com` to prevent HTTP 422 Unprocessable Entity errors.

### 3. Separation of Authority (Client vs. Server)
- **Client Web Workers** handle user-facing tasks: CSV parsing, fuzzy column mapping, font bounding box calculations, and live 60 FPS SVG preview.
- **Server Background Workers (ARQ)** handle authoritative tasks: high-DPI PDF generation (ReportLab/Playwright), Ed25519 signing, SHA-256 PDF hash sealing, and transactional email distribution.
- **Never** perform batch PDF generation inside the client browser.

### 4. Deterministic Cryptographic Proofs (RFC 8785)
When serializing W3C Verifiable Credentials or Open Badges 3.0:
- Use `app.credentials.canonicalizer.canonicalize_json()` to format JSON-LD payloads into RFC 8785 deterministic canonical byte streams prior to Ed25519 signature computation.
- Python dictionary key ordering or standard `json.dumps()` is non-deterministic across platforms and will break digital signatures.

---

## 7. Database Initialization & Seeding

To seed a fresh MongoDB instance with demo organizations, sample templates, and test users:

```powershell
cd e:\Certificate\Backend
.\.venv\Scripts\Activate.ps1

# Run the database migration and index creation
python -c "import asyncio; from app.core.database import init_db; asyncio.run(init_db())"
```

Default developer credentials created during local initialization:
- **Email**: `admin@certiflow.io`
- **Password**: `CertiFlowPass2026!`
- **Role**: `owner`
- **Organization**: `Acme University`

---

## 8. Docker Compose Deployment

To build and run the entire platform within isolated Docker containers:

```bash
# Build and launch all services in background
docker compose up -d --build

# View container logs
docker compose logs -f

# Check health status of all containers
docker compose ps

# Shut down and remove containers
docker compose down
```

The `docker-compose.yml` configures:
- `certiflow-api`: FastAPI backend container with Uvicorn worker pool
- `certiflow-worker`: ARQ background processing worker
- `certiflow-frontend`: Next.js production container (standalone output)
- `certiflow-mongo`: MongoDB 7.0 database container with health check
- `certiflow-redis`: Redis 7.2 container for task queue and caching
