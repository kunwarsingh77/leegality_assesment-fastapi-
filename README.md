# Network Route Optimization API

A FastAPI application to manage network nodes and edges, and find the shortest latency path between any two nodes using a custom path-finding algorithm.

Built with production-grade features: API versioning, rate limiting, response caching, CORS, security headers, input validation, and SQL injection protection.

## Prerequisites

Make sure you have the following installed before starting:

- Python 3.10 or higher
- MySQL 5.7 or higher (running locally)
- Git

---

## Local Setup — Step by Step

### Step 1 — Clone the repository

```bash
git clone <repo-url>
cd Leegality_Assesment_Project
```

---

### Step 2 — Create a virtual environment

```bash
python3 -m venv venv
```

Activate it:

```bash
# On Linux / macOS
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt once active.

---

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4 — Create the MySQL database

Log into MySQL:

```bash
mysql -u root -p
```

Then run:

```sql
CREATE DATABASE leegality_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

---

### Step 5 — Set up the `.env` file

Create a `.env` file in the project root:

```bash
touch .env
```

Open it and fill in your values:

```env
APP_ENV=development

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your%40password
DB_NAME=leegality_db

ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

MAX_REQUEST_BODY_SIZE=1048576
```

> **Important:** If your MySQL password contains special characters, URL-encode them.
> `@` must be written as `%40`.
>
> Example: password `Hello@1234` → write `Hello%401234` in the `.env` file.

---

### Step 6 — Run the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

The `--reload` flag auto-restarts the server on file changes.

On first startup, the app will **automatically create all required tables** in MySQL — no manual migration needed.

---

### Step 7 — Verify it's running

```bash
curl http://localhost:8001/health
```

Expected response:
```json
{ "status": "ok" }
```

---

## Explore the API

FastAPI comes with built-in interactive docs. Once the server is running, open:

Swagger UI (interactive) = http://localhost:8001/docs 
ReDoc (readable docs) - http://localhost:8001/redoc 

You can test every endpoint directly from the browser — no Postman needed.


# Project Structure (quick reference)

```
app/
├── api/v1/           → Versioned HTTP route handlers
├── services/         → Business logic
├── repositories/     → Database queries
├── models/           → SQLAlchemy table definitions
├── schemas/          → Pydantic request/response models + validation
├── db/               → DB engine and session setup
└── core/             → Config, exceptions, rate limiter, middleware
```

## Stopping the Server

Press `Ctrl + C` in the terminal where the server is running.

To deactivate the virtual environment:

```bash
deactivate
```
