# 06 – Setup and Testing

## Prerequisites
- Python 3.11+ and Node.js 20+ (LTS), Git
- Optional: a Google Gemini API key (free at https://aistudio.google.com) for live AI
- Optional: a Supabase project for PostgreSQL (SQLite is used automatically if `DATABASE_URL` is not set)

## Local installation
```bash
git clone https://github.com/<your-username>/cm-kerala-grievance-portal.git
cd cm-kerala-grievance-portal

# ---- backend ----
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate     macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env, then edit values
                            # (comment out DATABASE_URL to use local SQLite)
python -m app.cli load-reference-data      # departments (once)
python -m app.cli create-cmo --email you@example.com --mobile 9876543210   # asks for a password
python wsgi.py              # API on http://localhost:5000

# ---- frontend (second terminal) ----
cd frontend
npm install
npm run dev                 # app on http://localhost:5173 (proxies /api to :5000)
```
On first start the backend creates the tables in local SQLite. Nothing is seeded automatically. Log in with the CMO you created, then use **Officers** in the CMO dashboard to create officer accounts. To reset local data, delete `backend/instance/local.db`.

## Environment variables
| Variable | Where | Required | Description |
|---|---|---|---|
| `SECRET_KEY` | backend | yes (prod) | Long random string used to sign JWTs |
| `DATABASE_URL` | backend | yes (prod) | PostgreSQL URL (Supabase **Session pooler**). **Leave the variable unset (or commented out) locally** to use SQLite; an empty or placeholder value will fail to connect |
| `GEMINI_API_KEY` | backend | for live AI | Google AI Studio key |
| `GEMINI_MODEL` | backend | no | Default `gemini-3.8-flash`. Comma-separated list allowed; models are tried in order |
| `FRONTEND_ORIGIN` | backend | yes (prod) | Frontend URL allowed by CORS (comma-separated) |
| `JWT_EXPIRY_HOURS` | backend | no | Default 12 |
| `VITE_API_URL` | frontend | yes (prod) | Backend base URL, e.g. `https://cmk-grievance-api.onrender.com` |

See `.env.example`. **Never commit real secrets.** `.env` is git-ignored.

## Deployment (Render + Supabase)
1. **Supabase:** create a project (region Mumbai) → **Connect** → copy the **Session pooler** URI and put your DB password in it. Open **SQL Editor** and run, in order: `supabase/schema.sql`, `supabase/reference_data.sql`, and (test accounts for evaluators only) `supabase/demo_accounts.sql`. Tables should show as RLS-enabled, not "UNRESTRICTED".
2. **Gemini:** create an API key at aistudio.google.com.
3. **GitHub:** push this repository.
4. **Render:** New → **Blueprint** → select the repo. Render reads `render.yaml` and creates two services:
   - `cmk-grievance-api` → set `DATABASE_URL`, `GEMINI_API_KEY`, and `FRONTEND_ORIGIN` (the frontend URL, which you can fill in after step 5)
   - `cmk-grievance-portal` → set `VITE_API_URL` to the API URL (e.g. `https://cmk-grievance-api.onrender.com`)
5. When both are live, set `FRONTEND_ORIGIN` on the API to the portal URL and redeploy the API. If you changed `VITE_API_URL` after the first build, redeploy the portal (Vite reads it at build time).
6. Open `https://<api>/api/health` → `{"status":"ok"}`, then open the portal and log in with a demo account.

## Automated tests
```bash
cd backend
python -m pytest -v
```
The tests use an in-memory SQLite database and the labelled AI fallback, so no network or keys are needed. **16 tests, all passing.** The test database is built from the same `supabase/reference_data.sql` and `demo_accounts.sql`:

| # | Test | Verifies |
|---|---|---|
| 1 | `test_register_and_login` | Citizen registration returns a token; login works |
| 2 | `test_register_validation` | Bad name/email/mobile/password rejected with field errors |
| 3 | `test_wrong_password` | 401 for a wrong password |
| 4 | `test_protected_routes_need_token` | 401 without or with an invalid token |
| 5 | `test_citizen_cannot_use_cmo_endpoints` | 403 for role violations |
| 6 | `test_citizen_sees_only_own_grievances` | Citizens can't read others' grievances (404) |
| 7 | `test_officer_sees_only_department` | Officer sees a grievance only after it is forwarded to their department; other departments see nothing |
| 8 | `test_submit_generates_reference_and_ai` | Reference ID, attachment upload + download, AI fields, public tracking |
| 9 | `test_rejects_fake_file` | File content must match its extension |
| 10 | `test_track_unknown_reference` | 404 for an unknown reference |
| 11 | `test_end_to_end_workflow` | Submit → forward → internal remark → In Progress → ATR → CMO accept → Resolved → feedback → Reopened; internal remarks hidden from the citizen; every status in history with user and time |
| 12 | `test_invalid_transition_blocked` | Resolve without a remark is rejected |
| 13 | `test_stats` | Totals consistent; 14 districts |
| 14 | `test_ai_analyze_fallback_is_labelled` | Fallback is labelled "NOT AI output" and classifies correctly |
| 15 | `test_contact_saved` | Contact enquiry stored and visible to the CMO |
| 16 | `test_cmo_creates_officer` | Only the CMO can create officers; duplicate email and bad department rejected; new officer can log in |

## Manual test cases (on the hosted app)
| ID | Steps | Expected |
|---|---|---|
| M1 | Register a new citizen with mobile `12345` | Error: valid 10-digit mobile |
| M2 | Log in as `citizen@demo.com` → Submit grievance → fill in the subject/description → **Analyse with AI** | Suggestions with model name appear; "Apply" fills category and priority |
| M3 | Submit with a PDF attachment | Success message with reference number; grievance in dashboard |
| M4 | Logout → Track page → enter the reference | Status "Submitted" and history shown without login |
| M5 | Log in as `cmo@demo.com` → dashboard | Counts and 4 charts load; filters change the list (once grievances exist) |
| M5b | CMO → Officers → create an officer, log in as them | Officer sees only their department |
| M6 | Open the new grievance → view the attachment → Forward to the AI-suggested department | Status "Under Review"; history row added |
| M7 | Log in as the officer of that department (e.g. `officer.kseb@demo.com`) | Grievance visible; other departments' grievances not visible |
| M8 | Officer: Start investigation → submit an action-taken report | Status "In Progress"; report "Pending" |
| M9 | CMO: Accept report with a remark | Status "Resolved" |
| M10 | Citizen: open grievance → rate 5 stars → then Reopen with a reason | Feedback saved; status "Reopened"; CMO sees it again |
| M11 | CMO: add an internal remark; citizen views the grievance | Internal remark not visible to the citizen |
| M12 | Citizen tries `/cmo` in the URL | Redirected; API returns 403 for CMO endpoints |
| M13 | CMO: Escalate an overdue grievance | "Escalated" tag; priority High; history row |
| M14 | Contact page: send a message | Success; appears in CMO → Contact enquiries |
| M15 | Remove `GEMINI_API_KEY` and analyse | Orange "Fallback (not AI)" label shown |
