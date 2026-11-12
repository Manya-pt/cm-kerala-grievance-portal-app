# CM Kerala – Chief Minister's Public Grievance Redressal Portal

> **Recruitment prototype** built for the WhiteMatrix Software Solutions *AI Full Stack Engineer* machine test.
> Not affiliated with or endorsed by the Government of Kerala or the Chief Minister's Office. All data is fictional.

A working prototype where citizens submit grievances to the Chief Minister's Office (CMO), the CMO reviews and forwards them to departments, officers act and report back, and citizens track every step. An **AI Grievance Assistant** (Google Gemini) suggests the department, category and priority, writes a summary for the CMO and flags possible duplicates. A human always makes the final decision.

| | Link |
|---|---|
| **Live application** | `https://<your-frontend>.onrender.com` ← replace after deployment |
| **Backend API** | `https://<your-backend>.onrender.com/api/health` |
| **Demo video** | `<YouTube / Google Drive link>` |

> Free hosting sleeps when idle. The first request can take ~50 seconds to wake the server.

## Demo login credentials (test accounts only)

Password for every account: **`Demo@1234`**

| Role | Email |
|---|---|
| Citizen | `citizen@demo.com` (also `citizen2@demo.com`) |
| CMO Administrator | `cmo@demo.com` |
| Department Officer – Water Authority | `officer.kwa@demo.com` |
| Department Officer – Public Works | `officer.pwd@demo.com` |
| Other officers | `officer.<code>@demo.com` with code `kseb, health, edu, rev, home, sjd, lsgd, trans, agri` |

## Features
- **Public website:** Home (stats, featured departments), About Us, How It Works, Departments, Contact Us (saved to DB), FAQ, public Track page
- **Citizen portal:** register/login/logout, submit a grievance with district, category, subject, description and an optional image/PDF, unique reference number (`CMK-2026-000123`), dashboard with pending/resolved counts, remarks and status history, feedback after resolution, reopen
- **CMO dashboard:** total, pending, resolved and overdue counts; filters by district, category, priority, status, department and overdue; charts by status, district, department and month; forward to a department/officer; internal and public remarks; escalate delayed grievances; review action-taken reports (accept → Resolved, return → In Progress); re-run AI
- **Department officer dashboard:** sees only grievances forwarded to their department, starts the investigation, posts progress updates, submits an action-taken report with an optional file
- **Workflow and audit trail:** statuses `Submitted → Under Review → In Progress → Resolved → Reopened`. Every change is stored in `grievance_history` with timestamp and responsible user
- **AI Grievance Assistant:** Gemini LLM with JSON output, validated against the allowed lists. Duplicate detection combines text similarity with an LLM check. A clearly labelled fallback runs if the AI is unavailable
- **Security:** hashed passwords, JWT, role checks on every endpoint, ownership checks, file type and content validation, secrets only in environment variables

## Tech stack and reasons

| Layer | Choice | Why |
|---|---|---|
| Frontend | React 19 + Vite, React Router, Recharts | Component-based UI; one detail page adapts to each role; Recharts draws charts from live API data |
| Backend | Python 3 + Flask (REST API) | Small, explicit framework where each endpoint is a readable function; Python keeps business rules easy to follow |
| Database | PostgreSQL on Supabase (SQLite for local dev and tests) | Grievances, history, assignments and users are relational, so foreign keys keep the audit trail consistent |
| ORM | SQLAlchemy | Same code works on PostgreSQL and SQLite; protects against SQL injection |
| Auth | JWT (PyJWT) + Werkzeug password hashing | Stateless tokens suit a separate frontend; role stored in the token and re-checked from the DB |
| AI | Google Gemini API (free tier) | Real LLM with structured JSON output |
| Files | Stored in the database (`attachments` table) | Free hosting has no persistent disk; DB storage survives restarts and stays behind access control |
| Hosting | Render (API + static site) | Free, deploys from GitHub, public URLs |

## Project structure
```
backend/
  app/
    __init__.py        app factory, CORS, error handling, security headers
    config.py          settings from environment variables
    models.py          database tables
    auth.py            JWT creation + @login_required(role) decorator
    workflow.py        status transition rules + audit logging
    ai_service.py      AI Grievance Assistant (Gemini + labelled fallback)
    seed.py            fictional demo data
    routes/            auth, public, grievance, admin (stats/AI) endpoints
  tests/test_api.py    15 automated API tests
  wsgi.py              entry point
frontend/
  src/
    api.js, AuthContext.jsx, App.jsx
    components/        Layout, shared UI (badges, tables, timeline)
    pages/public/      Home, About, HowItWorks, Departments, Contact, FAQ, Track, Login, Register
    pages/citizen/     dashboard, submit grievance (with AI assistant)
    pages/cmo/         dashboard with charts, contact enquiries
    pages/officer/     dashboard
    pages/GrievanceDetail.jsx   role-specific actions
DOCUMENTATION/         01–07 docs + diagrams
render.yaml            deployment blueprint
```

## Quick start (local)
```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python wsgi.py                 # http://localhost:5000 (SQLite + demo data created automatically)
python -m pytest -v            # run tests

# frontend (new terminal)
cd frontend
npm install
npm run dev                    # http://localhost:5173
```
Add a `GEMINI_API_KEY` in `backend/.env` to enable live AI (see `.env.example`). Full instructions are in [DOCUMENTATION/06_Setup_and_Testing.md](DOCUMENTATION/06_Setup_and_Testing.md).

## Documentation
1. [Project Overview](DOCUMENTATION/01_Project_Overview.md)
2. [System Architecture](DOCUMENTATION/02_System_Architecture.md) (includes the architecture diagram)
3. [Database Design](DOCUMENTATION/03_Database_Design.md) (includes the ER diagram)
4. [API Documentation](DOCUMENTATION/04_API_Documentation.md)
5. [AI Integration](DOCUMENTATION/05_AI_Integration.md)
6. [Setup and Testing](DOCUMENTATION/06_Setup_and_Testing.md)
7. [User Guide](DOCUMENTATION/07_User_Guide.md)

## Tools and third-party services disclosure
- **AI coding assistant:** Claude (Anthropic) was used to help scaffold code and draft documentation. I reviewed, tested and can explain the implementation.
- **Runtime AI:** Google Gemini API (`gemini-3.8-flash`, free tier).
- **Services:** Supabase (PostgreSQL), Render (hosting), GitHub.
- **Open-source libraries:** Flask, Flask-SQLAlchemy, Flask-CORS, PyJWT, psycopg2, gunicorn, requests, python-dotenv, pytest, React, React Router, Axios, Recharts, Vite.

## Limitations and next steps
- Notifications are shown on the dashboard; email/SMS alerts are not implemented.
- Admin user management (creating officers) is done through seed data.
- Free-tier AI quotas can be exhausted; the labelled fallback then takes over.
- Future work: email/SMS notifications, Malayalam language support, officer SLA reports, rate limiting, object storage for large files.
