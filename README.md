# Library Management System API

A backend-only library management service built with FastAPI, SQLAlchemy, Pydantic, and SQLite. It exposes REST endpoints for catalog and member management, book lending and returns, overdue fines, and dashboard statistics.

## Features

- Create, browse, search, update, and archive books; check copy availability.
- Register, browse, update, filter, and archive members.
- Issue books only to active members and only when a copy is available.
- Prevent duplicate active loans of the same book to the same member.
- Record returns, restore inventory, and calculate overdue fines.
- Identify overdue loans from their due date.
- Paginate book, member, and active-loan lists.
- Enforce unique ISBNs and member email addresses.
- Preserve historical loans when a book or member is archived. An entity with an active loan cannot be archived.
- Return consistent JSON error bodies and expose Swagger UI and ReDoc.

## Technologies

Python 3.10+, FastAPI, SQLAlchemy 2, Pydantic 2, pydantic-settings, SQLite, pytest, and HTTPX.

## Project structure

```text
.
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── book_routes.py
│   │       ├── member_routes.py
│   │       ├── issue_routes.py
│   │       ├── return_routes.py
│   │       └── dashboard_routes.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── book.py
│   │   ├── member.py
│   │   └── issue.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── book_schema.py
│   │   ├── member_schema.py
│   │   ├── issue_schema.py
│   │   ├── return_schema.py
│   │   ├── common_schema.py
│   │   └── dashboard_schema.py
│   └── services/
│       ├── __init__.py
│       ├── book_service.py
│       ├── member_service.py
│       ├── issue_service.py
│       ├── return_service.py
│       ├── dashboard_service.py
│       └── common.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_books.py
│   ├── test_members.py
│   ├── test_issues.py
│   ├── test_returns.py
│   └── test_dashboard.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

The application creates its SQLite tables on startup. Issue and return operations update inventory and loan records in a single transaction. Book/member deletion is a soft archive so existing issue history remains intact.

## Prerequisites and installation

Install Python 3.10 or later. Run these commands from the project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell prevents virtual-environment activation, use the platform's standard execution-policy setup or invoke `.\.venv\Scripts\python.exe` directly.

## Configuration and database

Settings are read from environment variables (or `.env` in the working directory):

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `Library Management API` | FastAPI application title |
| `DATABASE_URL` | `sqlite:///./library.db` | SQLAlchemy database URL |
| `FINE_PER_DAY` | `1.0` | Fine in currency units per overdue day; must be non-negative |
| `LOAN_PERIOD_DAYS` | `14` | Loan period used to calculate due dates; must be positive |

Change `FINE_PER_DAY` in `.env` to configure the overdue fine (for example, `FINE_PER_DAY=2.5`). Returns on or before the due date have no fine. The default SQLite file is `library.db` in the current working directory; use an absolute SQLAlchemy SQLite URL if the process is launched elsewhere.

## Run the application

```powershell
uvicorn app.main:app --reload
```

The server listens at `http://127.0.0.1:8000`. Interactive API documentation is available at [Swagger UI](http://127.0.0.1:8000/docs) and [ReDoc](http://127.0.0.1:8000/redoc).

## API reference

All resource endpoints are prefixed with `/api/v1`. List endpoints return `{ "items": [...], "total": 0, "limit": 20, "offset": 0 }`; `limit` is 1–100 and `offset` is zero or greater.

### Books

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/books` | Add a book |
| `GET` | `/api/v1/books` | List books; optional `title`, `author`, `isbn`, `category` filters and pagination |
| `GET` | `/api/v1/books/search?q=tolkien` | Search title, author, ISBN, or category |
| `GET` | `/api/v1/books/{book_id}` | Get a book |
| `GET` | `/api/v1/books/{book_id}/availability` | Check available copies |
| `PUT` | `/api/v1/books/{book_id}` | Update provided book fields |
| `DELETE` | `/api/v1/books/{book_id}` | Archive a book (409 if it has an active loan) |

Example create request:

```json
{
  "title": "The Hobbit",
  "author": "J. R. R. Tolkien",
  "isbn": "9780547928227",
  "category": "Fantasy",
  "publisher": "Mariner Books",
  "published_year": 1937,
  "total_copies": 3
}
```

Successful create response (`201 Created`):

```json
{
  "id": 1,
  "title": "The Hobbit",
  "author": "J. R. R. Tolkien",
  "isbn": "9780547928227",
  "category": "Fantasy",
  "publisher": "Mariner Books",
  "published_year": 1937,
  "total_copies": 3,
  "available_copies": 3,
  "created_date": "2026-10-30"
}
```

Book update accepts any subset of the create fields. `total_copies` cannot be reduced below the number currently on loan; available copies are adjusted to preserve that invariant.

### Members

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/members` | Register a member |
| `GET` | `/api/v1/members` | List members; optional `membership_status` (`Active` or `Inactive`), `limit`, and `offset` |
| `GET` | `/api/v1/members/{member_id}` | Get a member |
| `PUT` | `/api/v1/members/{member_id}` | Update provided member fields |
| `DELETE` | `/api/v1/members/{member_id}` | Archive a member (409 if they have an active loan) |

Example member request:

```json
{
  "name": "Alex Reader",
  "email": "alex@example.com",
  "phone": "+1-555-0100",
  "address": "10 Library Lane",
  "membership_status": "Active"
}
```

### Issues and returns

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/issues` | Issue a book; JSON body: `{"book_id": 1, "member_id": 1}` |
| `GET` | `/api/v1/issues` | List current issued/overdue books; optional `member_id`, `limit`, and `offset` |
| `GET` | `/api/v1/issues/{issue_id}` | Get issue details |
| `POST` | `/api/v1/returns/{issue_id}` | Return the issue, restore inventory, and calculate any fine |
| `GET` | `/api/v1/returns/{issue_id}` | Get return and fine details (409 until returned) |

An issue response includes `id`, `book_id`, `member_id`, `issue_date`, `due_date`, `return_date`, `status`, and `fine_amount`. `status` is `Issued`, `Overdue`, or `Returned`. Return responses also include `overdue_days`.

### Dashboard

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/v1/dashboard` | Read total books, members, available copies, current issues, overdue books, and returns |

## Error responses

Errors use a common envelope:

```json
{
  "error": {
    "code": "HTTP_409",
    "message": "No copies of this book are currently available."
  }
}
```

Validation errors return `422` and include a `details` array with field locations. Common status codes are:

- `201` created; `200` successful read/update/action; `204` archived.
- `400` malformed request where applicable; `404` resource does not exist.
- `409` duplicate ISBN/email, unavailable or duplicate loan, invalid return, or blocked archive.
- `422` invalid request data; `500` unexpected server error.

## Testing in Postman

1. Start the server with `uvicorn app.main:app --reload`.
2. Create a Postman request to `http://127.0.0.1:8000/api/v1/books` using `POST`.
3. Set **Body → raw → JSON** and paste the book example above.
4. Create a member using `POST /api/v1/members`, then issue the book using `POST /api/v1/issues` with its returned IDs.
5. Use `GET /api/v1/issues` to view active loans and `POST /api/v1/returns/{issue_id}` to return one.
6. Browse the remaining endpoints in Swagger UI or call the URLs in the API reference directly. No authentication is configured.

## Testing in a browser

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) or [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) to inspect endpoint schemas and execute requests. For read-only requests, enter a GET URL such as `http://127.0.0.1:8000/api/v1/books` or `http://127.0.0.1:8000/api/v1/dashboard` in the browser address bar. Browser address bars cannot submit the JSON bodies required by POST/PUT; use Swagger UI or Postman for those.

## Run the tests

```powershell
pytest -q
```

Tests create an in-memory SQLite database and override the application's database dependency; they do not read or modify `library.db`.
