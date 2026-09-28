# CertiFlow — Backend Foundation (P0)

Enterprise FastAPI + MongoDB backend for automated certificate generation SaaS.

---

## 1. Technology Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
- **Database**: [MongoDB](https://www.mongodb.com/) (System Service / Local instance at `localhost:27017` or Atlas)
- **Async Driver**: [Motor](https://motor.readthedocs.io/) (`AsyncIOMotorClient`)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev/) + `pydantic-settings`
- **Security & Passwords**: Argon2id (`argon2-cffi`)
- **Authentication**: JWT access tokens + rotated SHA-256 hashed refresh tokens
- **Testing**: `pytest` + `pytest-asyncio` + `httpx` (25/25 automated tests)
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
│   │       └── health.py        # /health, /health/db
│   ├── models/                  # Domain entity definitions
│   ├── schemas/
│   │   ├── auth.py              # TokenResponse, AuthMeResponse, RefreshTokenRequest
│   │   ├── common.py            # APIResponse[T], APIErrorDetail
│   │   ├── organization.py      # OrganizationResponse, OrganizationUpdate, MemberResponse
│   │   └── user.py              # UserRegisterRequest, UserLoginRequest, UserResponse
│   ├── services/
│   │   ├── auth_service.py      # Registration, login, token rotation, logout
│   │   └── organization_service.py # Multi-tenant org isolation & RBAC checks
│   ├── repositories/
│   │   ├── user_repository.py         # MongoDB users collection queries
│   │   ├── organization_repository.py # MongoDB organizations & members queries
│   │   ├── refresh_token_repository.py# Rotated hashed token storage
│   │   └── audit_log_repository.py    # Audit logging for security compliance
│   └── middleware/
│       ├── request_id.py        # X-Request-ID propagation & HTTP access logging
│       └── error_handler.py     # Global exception handlers returning standardized envelopes
├── tests/
│   ├── conftest.py              # Async test client & isolated test DB fixtures
│   ├── unit/
│   │   ├── test_config.py       # Configuration & CORS parsing tests
│   │   └── test_security.py     # Argon2id & JWT token unit tests
│   └── integration/
│       ├── test_auth.py         # Full auth suite (register, login, refresh, logout)
│       ├── test_health.py       # Health & DB connectivity checks
│       └── test_organizations.py# Multi-tenant isolation & member tests
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

# 4. Start local development server
uvicorn app.main:app --reload --port 8000
```

Interactive Swagger Documentation:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 4. Running Automated Tests

```bash
# Run the full test suite
pytest -v
```

All 25 test cases run against the isolated `certificate_platform_test` database and teardown automatically.

---

## 5. API Response Protocol

### Success Standard (`200 OK` / `201 Created`)
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "6aba0cca3979f6da1f6ab50b",
      "email": "atul@example.com",
      "name": "Atul",
      "is_active": true,
      "email_verified": false,
      "created_at": "2026-09-28T12:00:00Z"
    }
  },
  "error": null
}
```

### Error Standard (`400`, `401`, `403`, `404`, `409`, `422`)
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "DUPLICATE_EMAIL",
    "message": "A user with this email address already exists",
    "details": null
  }
}
```

---

## 6. Docker Deployment

```bash
# Start backend and MongoDB together
docker-compose up --build -d

# Check logs
docker-compose logs -f certificate-api
```
