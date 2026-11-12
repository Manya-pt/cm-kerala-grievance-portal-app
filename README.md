# CM Kerala – Chief Minister's Public Grievance Redressal Portal

> **Recruitment prototype** built for the WhiteMatrix Software Solutions *AI Full Stack Engineer* machine test.
> Not affiliated with or endorsed by the Government of Kerala or the Chief Minister's Office. All data is fictional.

Citizens submit grievances to the Chief Minister's Office (CMO). The CMO reviews and forwards them to departments, officers act and submit action-taken reports, and citizens track every step. An **AI Grievance Assistant** (Google Gemini) suggests the department, category and priority, writes a summary for the CMO and flags possible duplicates. A human always makes the final decision.

| | Link |
|---|---|
| **Live application** | https://cmk-grievance-portal.onrender.com |
| **Backend API** | https://cmk-grievance-api.onrender.com/api/health |
| **Demo video** | _add link here_ |

> Free hosting sleeps when idle. The first request can take ~50 seconds.

## Demo login credentials (test accounts only)

Created by `supabase/demo_accounts.sql` (explicit SQL, not run automatically). Password for every account: **`Demo@1234`**

| Role | Email |
|---|---|
| Citizen | `citizen@demo.com` (also `citizen2@demo.com`) |
| CMO Administrator | `cmo@demo.com` |
| Department Officer – Water Authority | `officer.kwa@demo.com` |
| Department Officer – Public Works | `officer.pwd@demo.com` |
| Other officers | `officer.<code>@demo.com` with code `kseb, health, edu, rev, home, sjd, lsgd, trans, agri` |

## Tech stack
React (Vite) · Flask (Python REST API) · PostgreSQL on Supabase · SQLAlchemy · JWT with role-based access · Google Gemini API · Render hosting.
Reasons for each choice are in [DOCUMENTATION/02_System_Architecture.md](DOCUMENTATION/02_System_Architecture.md).

## Run locally
```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m app.cli load-reference-data   # departments (once)
python -m app.cli create-cmo --email you@example.com --mobile 9876543210   # first CMO (asks for a password)
python wsgi.py                 # http://localhost:5000 (local SQLite, tables created automatically)
python -m pytest -v            # 16 tests

# frontend (new terminal)
cd frontend
npm install
npm run dev                    # http://localhost:5173
```
Copy `backend/.env.example` to `backend/.env`, keep `DATABASE_URL` commented out (SQLite). For Supabase, run `supabase/schema.sql`, `reference_data.sql` and (for evaluator logins) `demo_accounts.sql` in its SQL Editor and add a `GEMINI_API_KEY` to enable live AI. More detail: [DOCUMENTATION/06_Setup_and_Testing.md](DOCUMENTATION/06_Setup_and_Testing.md).

## Documentation
1. [Project Overview](DOCUMENTATION/01_Project_Overview.md)
2. [System Architecture](DOCUMENTATION/02_System_Architecture.md) (architecture diagram)
3. [Database Design](DOCUMENTATION/03_Database_Design.md) (ER diagram)
4. [API Documentation](DOCUMENTATION/04_API_Documentation.md)
5. [AI Integration](DOCUMENTATION/05_AI_Integration.md)
6. [Setup and Testing](DOCUMENTATION/06_Setup_and_Testing.md)
7. [User Guide](DOCUMENTATION/07_User_Guide.md)

## Tools and services disclosure
- **AI coding assistants:** Claude (Anthropic) and ChatGPT (OpenAI), used for scaffolding, debugging and documentation. I reviewed and tested the code and can explain it.
- **Runtime AI:** Google Gemini API (free tier). `GEMINI_MODEL` takes a comma-separated list of models, tried in order.
- **Services:** Supabase (PostgreSQL), Render (hosting), GitHub.
- **Libraries:** Flask, Flask-SQLAlchemy, Flask-CORS, PyJWT, psycopg2, gunicorn, requests, pytest, React, React Router, Axios, Recharts, Vite.

