# 03 – Database Design

PostgreSQL (Supabase) in production, SQLite locally. Defined with SQLAlchemy in `backend/app/models.py`. Tables are created automatically at start-up.

## ER diagram
```mermaid
erDiagram
    USERS ||--o{ GRIEVANCES : "submits (citizen)"
    DEPARTMENTS ||--o{ USERS : "employs (officer)"
    DEPARTMENTS ||--o{ GRIEVANCES : "is responsible for"
    GRIEVANCES ||--o{ GRIEVANCE_HISTORY : "has"
    USERS ||--o{ GRIEVANCE_HISTORY : "performed by"
    GRIEVANCES ||--o{ ASSIGNMENTS : "forwarded via"
    DEPARTMENTS ||--o{ ASSIGNMENTS : "receives"
    USERS ||--o{ ASSIGNMENTS : "officer / assigned_by"
    GRIEVANCES ||--o{ ATTACHMENTS : "has"
    ACTION_REPORTS ||--o{ ATTACHMENTS : "has"
    GRIEVANCES ||--o{ ACTION_REPORTS : "has"
    USERS ||--o{ ACTION_REPORTS : "written by officer"
    GRIEVANCES ||--o| FEEDBACK : "receives"
    USERS ||--o{ FEEDBACK : "given by citizen"

    USERS {
        int id PK
        string name
        string email UK
        string mobile
        string password_hash
        string role "citizen | cmo | officer"
        int department_id FK "officers only"
        datetime created_at
    }
    DEPARTMENTS {
        int id PK
        string name UK
        string code UK
        text description
    }
    GRIEVANCES {
        int id PK
        string ref_id UK "CMK-YYYY-NNNNNN"
        int citizen_id FK
        string district
        string category
        string subject
        text description
        string priority "Low | Medium | High"
        string status "Submitted | Under Review | In Progress | Resolved | Reopened"
        int department_id FK
        bool escalated
        datetime due_at
        datetime created_at
        datetime updated_at
        datetime resolved_at
        string ai_department
        string ai_category
        string ai_priority
        text ai_summary
        string ai_duplicate_ref
        text ai_duplicate_reason
        string ai_source
    }
    GRIEVANCE_HISTORY {
        int id PK
        int grievance_id FK
        string from_status
        string to_status
        string action
        text remark
        bool is_internal
        int user_id FK
        datetime created_at
    }
    ASSIGNMENTS {
        int id PK
        int grievance_id FK
        int department_id FK
        int officer_id FK
        int assigned_by_id FK
        text note
        bool active
        datetime assigned_at
    }
    ATTACHMENTS {
        int id PK
        int grievance_id FK
        int report_id FK "set for ATR files"
        string filename
        string mimetype
        int size
        binary data
        string kind "supporting | atr"
        int uploaded_by_id FK
        datetime created_at
    }
    ACTION_REPORTS {
        int id PK
        int grievance_id FK
        int officer_id FK
        text report
        string review_status "Pending | Accepted | Returned"
        text cmo_remark
        datetime created_at
        datetime reviewed_at
    }
    FEEDBACK {
        int id PK
        int grievance_id FK,UK
        int citizen_id FK
        int rating "1-5"
        text comment
        datetime created_at
    }
    CONTACT_ENQUIRIES {
        int id PK
        string name
        string email
        string subject
        text message
        datetime created_at
    }
```
A standalone copy is in [diagrams/er_diagram.md](diagrams/er_diagram.md).

## Tables
| Table | Purpose | Key points |
|---|---|---|
| `users` | Citizens, CMO admins and officers in one table | `role` column; `department_id` only for officers; unique email; hashed password |
| `departments` | Government departments (fictional sample) | Unique `name` and `code` (PWD, KWA, KSEB …) |
| `grievances` | The complaint | Unique `ref_id`; official `priority/category/department` stored **separately** from `ai_*` suggestions so human decisions and AI output are never mixed |
| `grievance_history` | Audit trail | One row per action: from/to status, remark, user, timestamp, `is_internal` |
| `assignments` | Forwarding records | Every forward is kept; `active` marks the current one, so re-assignments are traceable |
| `attachments` | Uploaded files | Bytes stored in the DB (persist on free hosting, protected by access checks); `kind` separates citizen evidence from ATR files |
| `action_reports` | Officer's action-taken report | CMO review result and remark |
| `feedback` | Citizen rating after resolution | One per grievance (unique FK) |
| `contact_enquiries` | Contact Us form | Public submissions, visible to the CMO |

## Relationships
- A **citizen** has many grievances; a grievance belongs to one citizen.
- A **department** has many officers and many grievances.
- A grievance has many **history** rows, **assignments**, **attachments** and **action reports**, and at most one **feedback**.
- An action report can have attachments (`attachments.report_id`).
- Deleting a grievance cascades to its child rows (configured in SQLAlchemy).

## Design decisions
- **Relational model.** Workflow data is strongly connected (user ↔ grievance ↔ department ↔ history), so foreign keys and transactions keep it consistent.
- **Single users table with roles.** Simple authentication; officer-only data is a nullable FK.
- **History as an append-only log.** Status changes are never overwritten, so the full lifecycle can be traced (a mandatory requirement).
- **Overdue is computed, not stored:** `status != Resolved AND now > due_at`. `due_at` = created + 3/7/14 days (High/Medium/Low), reset on reopen.
- **Indexes** on `users.email`, `grievances.ref_id`, `grievances.status` and `grievance_history.grievance_id` for frequent lookups.
- **Reference number** `CMK-<year>-<id padded to 6>` is unique and generated after insert.

## Sample data
`backend/app/seed.py` inserts 11 departments, 1 CMO admin, 11 officers, 2 citizens, 22 grievances in every status (with history, assignments, reports, feedback, one escalation and one duplicate pair) and 2 contact enquiries. All data is fictional.
