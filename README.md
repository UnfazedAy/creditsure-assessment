# CrediSure Dashboard API

CrediSure is a backend-focused assessment project for user authentication,
administrative user management, and dashboard statistics. It exposes a REST API
for a dashboard client; it does not include a browser-based frontend.

## Demo Administrator Access

The deployed assessment API and Swagger UI are available at
[creditsure-assessment-production.up.railway.app/docs](https://creditsure-assessment-production.up.railway.app/docs).

| Item | Assessment demo |
|---|---|
| Login endpoint | `POST /api/v1/auth/login` |
| Email | `admin@credisure.com` |
| Password | `Password123@` |

In Swagger, submit the email and password to the login endpoint. Copy
`data.access_token` from the response, click **Authorize**, and paste the token
into the HTTP Bearer field; Swagger adds the `Bearer` prefix to protected
requests.

These credentials are exclusively for this assessment. The account has
administrator permissions over fictional assessment records, but no access to
Railway infrastructure, secrets, or unrelated systems. Do not reuse the
password for any real application. Rotate it or disable the account after
assessment review.

## Features

- User registration and login with Argon2 password hashing.
- JWT bearer authentication with access and refresh tokens in the login response.
- Authenticated profile retrieval and admin-role authorization.
- Admin-only user listing, UUID lookup, and account activation/deactivation.
- Case-insensitive search, role and activity filters, and bounded pagination.
- Database-backed total, active, inactive, and current-month user counts.
- Health endpoint, request timing header, and consistent validation/error responses.
- SQLAlchemy persistence with SQLite by default and optional PostgreSQL/MySQL URLs.

User email addresses are unique. Full names are not unique; multiple users may
share the same name.

## Technology

The project uses Python 3.10 or later (the current development environment uses
Python 3.12), FastAPI 0.162.0, SQLAlchemy 2.1.8, Pydantic 2.14.2,
pydantic-settings 2.16.2, PyJWT 2.15.1, pwdlib 0.3.1 with Argon2,
and Uvicorn 0.54.0. SQLite is the default database. Pytest 9.2.0, HTTPX
0.28.1, and pytest-cov 7.1.0 are used for testing. The versions above reflect
the current project environment; see [requirements.txt](./requirements.txt)
for the reproducible dependency set.

## Project layout

```text
app/
├── core/           Configuration, JWT/password helpers, exception handlers
├── db/             SQLAlchemy engine, session, and declarative base
├── dependencies/   Authentication and role authorization dependencies
├── middleware/     Request logging and response timing
├── models/         SQLAlchemy models
├── routers/        HTTP route definitions
├── schemas/        Pydantic request and response models
├── scripts/        One-off administrator and demo-user commands
├── services/       Authentication, user, and dashboard operations
├── utils/          Pagination helpers
└── main.py         FastAPI application and router registration
tests/              Isolated API and script tests
```

Routers validate and route HTTP requests; services implement application
operations; schemas define validated API shapes; models describe database
tables; dependencies authenticate and authorize requests; middleware logs
request timing; core modules provide settings, security helpers, and exception
handlers. The scripts provision users explicitly and are never run at API
startup.

## Prerequisites

- Python 3.10 or later.
- SQLite is included with Python and needs no separate server.
- For optional PostgreSQL, a PostgreSQL server/database and the `psycopg`
  driver are required. For optional MySQL, a MySQL server/database and the
  `PyMySQL` driver are required; both drivers are included in `requirements.txt`.

## Local setup

Clone and enter the repository:

```bash
git clone https://github.com/UnfazedAy/creditsure-assessment.git
cd creditsure-assessment
```

Create and activate a virtual environment.

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS Bash:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies and create a local environment file:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux/macOS Bash:

```bash
cp .env.example .env
```

Generate a signing secret and replace the example `SECRET_KEY` in `.env` with
the generated value:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Do not commit `.env` or use the example placeholder as a production secret.
The application requires a configured `SECRET_KEY`.

The application creates missing tables on startup. To initialize the configured
database without starting the API:

```bash
python -c "from app.db.database import Base, engine; from app.models.user import User; Base.metadata.create_all(bind=engine)"
```

`create_all` creates missing tables but does not migrate existing schemas.
Alembic migrations are not currently implemented.

Start the API from the repository root:

```bash
uvicorn app.main:app --reload
```

or

```bash
fastapi dev app/main.py
```

The API is available at `http://127.0.0.1:8000`. Open
`http://127.0.0.1:8000/docs` for Swagger UI or
`http://127.0.0.1:8000/redoc` for ReDoc.

## Configuration

Settings are loaded from environment variables and the root `.env` file.
Environment values take precedence. `SECRET_KEY` must be supplied.

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `APP_NAME` | No | `CrediSure Dashboard API` | FastAPI application title |
| `ENVIRONMENT` | No | `development` | Environment name; `production`/`prod` enables seed guard |
| `DATABASE_URL` | No | `sqlite:///./credisure.db` | SQLAlchemy database URL |
| `SECRET_KEY` | Yes | — | Secret for signing and validating JWTs |
| `ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | Access-token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | `7` | Refresh-token lifetime |
| `DEMO_USER_PASSWORD` | No | Prompted when seeding | Password assigned to newly seeded demo accounts |
| `ALLOW_DEMO_SEEDING` | No | `false` | Explicitly permits demo seeding in production |
| `ADMIN_FULL_NAME` | No | Prompted when omitted | Non-interactive admin provisioning |
| `ADMIN_EMAIL` | No | Prompted when omitted | Non-interactive admin provisioning |
| `ADMIN_PASSWORD` | No | Prompted when omitted | Non-interactive admin provisioning |

Set all three `ADMIN_*` values together; partial configuration is rejected.
Keep deployment secrets in the hosting provider's secret/environment settings,
not in source control. FastAPI debug trace responses are disabled so unexpected
exceptions do not expose stack traces to API clients.

## Database

SQLite is the default and requires no separate service:

```dotenv
DATABASE_URL=sqlite:///./credisure.db
```

The SQLite file is relative to the process working directory. SQLAlchemy uses
SQLite-specific thread settings only for SQLite URLs and enables connection
health checks. A database URL explicitly set to PostgreSQL or MySQL is not
silently replaced if its connection fails.

Optional PostgreSQL:

```dotenv
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/credisure_db
```

Optional MySQL:

```dotenv
DATABASE_URL=mysql+pymysql://USER:PASSWORD@localhost:3306/credisure_db
```

Create the target database and database user on the server before starting the
API. URL-encode special characters in usernames or passwords. SQLAlchemy's
portable `Uuid` type stores UUID4 user identifiers across the supported
database engines.

The app and provisioning scripts create missing tables with SQLAlchemy
`metadata.create_all`; this is not a schema migration system.

## API reference

All API routes are under `/api/v1`. Authentication uses
`Authorization: Bearer <access_token>`. The documentation pages `/docs` and
`/redoc` are generated by FastAPI.

| Method and path | Purpose | Authentication |
|---|---|---|
| `GET /api/v1/health` | Service health response | Public |
| `POST /api/v1/auth/register` | Register a regular user | Public |
| `POST /api/v1/auth/login` | Verify credentials and return JWTs | Public |
| `GET /api/v1/auth/me` | Return the authenticated profile | Any active user |
| `GET /api/v1/users` | Search/filter/paginate users | Admin |
| `GET /api/v1/users/{user_id}` | Get a user by UUID | Admin |
| `PATCH /api/v1/users/{user_id}` | Change a user's active state | Admin |
| `GET /api/v1/dashboard/overview` | Return dashboard statistics | Admin |

### Registration

`POST /api/v1/auth/register` accepts:

```json
{
  "full_name": "Jordan Lee",
  "email": "jordan@example.com",
  "password": "AtLeast8Characters"
}
```

`full_name` must be 2-150 characters, `email` must be valid, and `password`
must be 8-128 characters. Registration returns `201 Created` with the public
user profile (id, name, email, role, active state, creation time) inside the
standard response envelope. It does not return a password or password hash.
Duplicate email returns `409 Conflict`; invalid input returns `422
Unprocessable Entity`.

```json
{
  "success": true,
  "data": {
    "id": "d44af641-2708-45ce-8e3f-5e58af40736a",
    "full_name": "Jordan Lee",
    "email": "jordan@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2026-11-05T12:00:00Z"
  },
  "detail": "User registered successfully"
}
```

All successful operations use `success: true`, a typed result in `data`, and a
human-readable endpoint-specific `detail`. Errors use `success: false`,
`data: null`, and a safe `detail`; validation errors can also include field
errors.

### Login and profile

`POST /api/v1/auth/login` accepts `{"email":"jordan@example.com",
"password":"AtLeast8Characters"}`. A successful response (`200 OK`) contains
the existing `access_token`, `refresh_token`, and `token_type` under `data`:

```json
{
  "success": true,
  "data": {
    "access_token": "<generated-access-token>",
    "refresh_token": "<generated-refresh-token>",
    "token_type": "bearer"
  },
  "detail": "Login successful"
}
```

Use the access token as a bearer token. The access token expires after
`ACCESS_TOKEN_EXPIRE_MINUTES`; the refresh token's configured lifetime is
`REFRESH_TOKEN_EXPIRE_DAYS`. A refresh endpoint is not implemented.

Invalid credentials return `401 Unauthorized`; an inactive account returns
`403 Forbidden`. An empty password returns `400`; malformed or missing request
fields return `422`. `GET /api/v1/auth/me` returns the authenticated profile
under `data`, with detail `"User retrieved successfully"`, or `401` for
missing/invalid credentials and `403` for an inactive account.

### Admin user management

`GET /api/v1/users` accepts these query parameters:

| Parameter | Default | Constraint / meaning |
|---|---:|---|
| `page` | `1` | At least 1 |
| `limit` | `10` | 1-100 results per page |
| `search` | — | Optional, up to 100 characters; case-insensitive name/email search |
| `is_active` | — | Optional boolean filter |
| `role` | — | Optional `user` or `admin` filter |

Example:

```text
GET /api/v1/users?page=2&limit=5&search=jordan&is_active=true&role=user
```

The pagination fields are inside `data`, which contains `items`, `total`,
`page`, `limit`, `total_pages`, `has_next`, and `has_previous`. Each item
contains the public user profile. The outer envelope's detail is
`"Users retrieved successfully"`.

```json
{
  "success": true,
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "limit": 10,
    "total_pages": 0,
    "has_next": false,
    "has_previous": false
  },
  "detail": "Users retrieved successfully"
}
```

Invalid parameters return `422`. These routes require an active administrator;
missing/invalid authentication returns `401`, and a regular user's request
returns `403`.

`GET /api/v1/users/{user_id}` accepts a UUID4 and returns one profile (`200`),
inside `data` with detail `"User retrieved successfully"`, or `404` when it
does not exist. Invalid UUID input returns `422`.

```json
{
  "success": true,
  "data": {
    "id": "d44af641-2708-45ce-8e3f-5e58af40736a",
    "full_name": "Jordan Lee",
    "email": "jordan@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2026-11-05T12:00:00Z"
  },
  "detail": "User retrieved successfully"
}
```

`PATCH /api/v1/users/{user_id}` accepts:

```json
{"is_active": false}
```

It returns the updated public profile inside `data` (`200`) with detail
`"User updated successfully"`. An admin cannot deactivate their own account
(`400`); a missing user returns `404`, and invalid input returns `422`.

### Dashboard overview

`GET /api/v1/dashboard/overview` is admin-only. Its database aggregation
returns total, active, and inactive user counts plus the number of users
created since the beginning of the current month:

```json
{
  "success": true,
  "data": {
    "total_users": 11,
    "active_users": 8,
    "inactive_users": 3,
    "new_users_this_month": 6
  },
  "detail": "Dashboard overview retrieved successfully"
}
```

Counts are illustrative. The endpoint returns `200` for an authorized admin,
`401` without valid authentication, and `403` for a non-admin.

### Health and errors

`GET /api/v1/health` is public and returns:

```json
{
  "success": true,
  "data": {"status": "healthy", "service": "dashboard-api"},
  "detail": "Service is healthy"
}
```

HTTP errors use `{"success": false, "data": null, "detail": "..."}`. Request
validation errors additionally include field-level `errors` containing field
locations and safe messages, not raw submitted values. Unhandled exceptions are
logged server-side and return a generic `500` detail; internal exception
details are not included in the response.

Example validation error:

```json
{
  "success": false,
  "data": null,
  "detail": "Request validation failed",
  "errors": [
    {"field": "body.email", "message": "value is not a valid email address"}
  ]
}
```

Status codes used by the API include `200` for successful reads/updates/login,
`201` for registration, `400` for attempts to deactivate the current admin,
`401` for authentication failures, `403` for inactive users or insufficient
role, `404` for missing users/routes, `409` for duplicate registration,
`422` for request validation, and `500` for unhandled server errors.

## Authentication and authorization

Passwords are hashed with Argon2 via pwdlib. Login issues JWT access and
refresh tokens containing the user's UUID string as the subject and their
role as a claim. Protected routes decode the token, validate the access-token
type and UUID subject, then load the current user from the database. User
listing, user lookup/update, and dashboard statistics require the `admin` role.
There is no public administrator-creation endpoint.

In Swagger UI, call login, copy `data.access_token`, select **Authorize**, and
paste the access token into the HTTP Bearer field. Swagger adds the `Bearer`
prefix. Password hashes are excluded from API response schemas.

## Administrator and demo accounts

Create an administrator explicitly; the script prompts for a name, email, and
password, with the password entered securely:

```bash
python -m app.scripts.create_admin
```

For non-interactive provisioning, set `ADMIN_FULL_NAME`, `ADMIN_EMAIL`, and
`ADMIN_PASSWORD` in the environment or an uncommitted `.env` file. All three
must be present. Re-running for an existing admin email makes no changes. The
script refuses to promote an existing regular account.

Create 10 fictional regular accounts with realistic names and
`@example.com` addresses:

```bash
python -m app.scripts.seed_users
```

If `DEMO_USER_PASSWORD` is unset, the script prompts for a password and
confirmation. Newly created demo users share that configured password; it must
be 8-128 characters. Existing accounts are identified by their stable emails
and are skipped without changing their role, status, or password. The script
does not delete users and is not run automatically by the API.

In production (`ENVIRONMENT=production` or `prod`), seeding is refused unless
`ALLOW_DEMO_SEEDING=true` is explicitly set. Only enable this for an
assessment deployment that intentionally needs demo accounts. The assessment
administrator credentials are listed in [Demo Administrator Access](#demo-administrator-access)
above. This admin can perform account-status updates on the fictional
assessment data; no read-only reviewer role is implemented. Rotate the
password or disable the account after review.

## Testing

Run the full test suite:

```bash
python -m pytest tests/ -v
```

Run a specific module:

```bash
python -m pytest tests/test_auth.py -v
python -m pytest tests/test_users.py -v
python -m pytest tests/test_dashboard.py -v
python -m pytest tests/test_health.py -v
python -m pytest tests/test_scripts.py -v
```

Run coverage:

```bash
python -m pytest tests/ --cov=app --cov-report=term-missing
```

API tests use an in-memory SQLite database and a dependency override for each
test; they do not use or reset the configured application database. Script
logic tests pass the isolated test session directly.

## Deployment

### Railway with Docker

The root `Dockerfile` is detected by Railway automatically. Connect the
repository and deploy from its root; no `railway.json`, Docker Compose file,
or custom build command is required. The container starts Uvicorn on
Railway's `PORT` environment variable (falling back to `8000` locally).

In the Railway service's **Variables**, configure at least:

```text
SECRET_KEY=<generated secure value>
ENVIRONMENT=production
```

For durable data, use a Railway PostgreSQL service and set `DATABASE_URL` to
the connection URL Railway provides. If you choose SQLite, add a Railway
Volume mounted at `/data` and set:

```text
DATABASE_URL=sqlite:////data/credisure.db
```

Without a persistent volume, SQLite data stored in the container can be lost
on redeploy or restart. SQLite is also not a good fit for multiple app replicas
sharing write traffic; use PostgreSQL in that case. The API creates missing
tables at startup. Provision an administrator as a one-off command with
`python -m app.scripts.create_admin`; do not place admin credentials in the
Docker image or source repository. If demo users are needed, run the seed
script explicitly and set `ALLOW_DEMO_SEEDING=true` only for that operation.

The service health-check path is `/api/v1/health`. After deployment, Railway
provides the public URL; append `/docs` for Swagger UI if it is enabled.

To build and run the same image locally (requires Docker):

```bash
docker build -t creditsure-api .
docker run --rm -p 8000:8000 --env-file .env creditsure-api
```

`.dockerignore` keeps local environment files, virtual environments, tests, and
SQLite files out of the image. Configure secrets separately in Railway.

### Other deployment notes

1. Install the pinned dependencies from `requirements.txt`.
2. Set `SECRET_KEY`, `DATABASE_URL`, and token settings through the platform's
   environment/secret configuration. Framework debug trace responses are
   disabled.
3. Ensure the selected database is reachable and initialized. The app creates
   missing tables at startup; provisioning scripts also create missing tables.
4. Create an admin with `python -m app.scripts.create_admin` as a one-off
   command/job. Seed demo users only if the assessment needs them.
5. Start with a platform-assigned port:

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
   ```

6. Configure the platform health probe to request `/api/v1/health`. Swagger UI
   is available at `/docs` unless the host restricts it.

SQLite is convenient for local use, but hosted filesystems may be ephemeral.
On such platforms the SQLite file and its users may disappear after a restart
or redeploy. Use a persistent volume where supported, or choose PostgreSQL
when durable SQLite storage is unavailable. Do not assume a provider persists
local files. The app does not download the developer's local database during
deployment. The current CORS configuration allows all origins; restrict
origins in a deployment that serves a browser client from a known domain.

## Security notes

Implemented protections include Argon2 password hashing, signed and validated
JWTs, access-token type checks, UUID subject validation, role checks, Pydantic
request validation, generic unhandled-error responses, and response schemas
that omit password hashes. Keep signing and administrator/demo credentials
outside source control and use HTTPS in deployment. CORS is currently
permissive and should be restricted if a browser client is deployed.

## Design and assessment scope

FastAPI provides typed API routes and OpenAPI documentation. SQLAlchemy keeps
database operations behind the model/session boundary, and UUID4 identifiers
avoid exposing sequential database IDs. Routers and services separate HTTP
contracts from application operations. SQLite makes local setup self-contained;
PostgreSQL and MySQL remain optional through SQLAlchemy URLs and their drivers.
The dashboard endpoint is admin-oriented because it exposes cross-user
statistics. No frontend is included: the implementation focuses on backend
responsibilities for login, dashboard data, user listing/search/filtering,
request status, and account management. It does not claim to provide visual
navigation or responsive UI behavior.

Possible future work includes Alembic migrations, configurable CORS origins,
rate limiting, and additional deployment monitoring. These are not currently
implemented features.
