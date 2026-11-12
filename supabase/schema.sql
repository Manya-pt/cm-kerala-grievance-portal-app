-- CM Kerala Grievance Portal: database schema for Supabase (PostgreSQL).
-- Run this once in Supabase -> SQL Editor, then run reference_data.sql.
-- It mirrors backend/app/models.py. Timestamps are stored as UTC.

CREATE TABLE IF NOT EXISTS departments (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(120) NOT NULL UNIQUE,
    code        VARCHAR(20)  NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(120) NOT NULL,
    email         VARCHAR(160) NOT NULL UNIQUE,
    mobile        VARCHAR(15),
    password_hash VARCHAR(256) NOT NULL,
    role          VARCHAR(20)  NOT NULL DEFAULT 'citizen'
                  CHECK (role IN ('citizen', 'cmo', 'officer')),
    department_id INTEGER REFERENCES departments(id),   -- officers only
    created_at    TIMESTAMP DEFAULT (now() AT TIME ZONE 'utc'),
    CHECK ((role = 'officer') = (department_id IS NOT NULL))
);
CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);

CREATE TABLE IF NOT EXISTS grievances (
    id            SERIAL PRIMARY KEY,
    ref_id        VARCHAR(30) UNIQUE,                    -- CMK-YYYY-NNNNNN
    citizen_id    INTEGER NOT NULL REFERENCES users(id),
    district      VARCHAR(40)  NOT NULL,
    category      VARCHAR(60)  NOT NULL,
    subject       VARCHAR(200) NOT NULL,
    description   TEXT NOT NULL,
    priority      VARCHAR(10) DEFAULT 'Medium' CHECK (priority IN ('Low', 'Medium', 'High')),
    status        VARCHAR(20) DEFAULT 'Submitted'
                  CHECK (status IN ('Submitted', 'Under Review', 'In Progress', 'Resolved', 'Reopened')),
    department_id INTEGER REFERENCES departments(id),
    escalated     BOOLEAN DEFAULT FALSE,
    due_at        TIMESTAMP,
    created_at    TIMESTAMP DEFAULT (now() AT TIME ZONE 'utc'),
    updated_at    TIMESTAMP DEFAULT (now() AT TIME ZONE 'utc'),
    resolved_at   TIMESTAMP,
    -- AI suggestions, kept apart from the official values above
    ai_department       VARCHAR(120),
    ai_category         VARCHAR(60),
    ai_priority         VARCHAR(10),
    ai_summary          TEXT,
    ai_duplicate_ref    VARCHAR(30),
    ai_duplicate_reason TEXT,
    ai_source           VARCHAR(40)
);
CREATE INDEX IF NOT EXISTS ix_grievances_ref_id ON grievances (ref_id);
CREATE INDEX IF NOT EXISTS ix_grievances_status ON grievances (status);
CREATE INDEX IF NOT EXISTS ix_grievances_citizen ON grievances (citizen_id);
CREATE INDEX IF NOT EXISTS ix_grievances_department ON grievances (department_id);

CREATE TABLE IF NOT EXISTS grievance_history (
    id           SERIAL PRIMARY KEY,
    grievance_id INTEGER NOT NULL REFERENCES grievances(id) ON DELETE CASCADE,
    from_status  VARCHAR(20),
    to_status    VARCHAR(20),
    action       VARCHAR(60) NOT NULL,
    remark       TEXT,
    is_internal  BOOLEAN DEFAULT FALSE,                  -- hidden from citizens
    user_id      INTEGER REFERENCES users(id),
    created_at   TIMESTAMP DEFAULT (now() AT TIME ZONE 'utc')
);
CREATE INDEX IF NOT EXISTS ix_history_grievance ON grievance_history (grievance_id);

CREATE TABLE IF NOT EXISTS assignments (
    id             SERIAL PRIMARY KEY,
    grievance_id   INTEGER NOT NULL REFERENCES grievances(id) ON DELETE CASCADE,
    department_id  INTEGER NOT NULL REFERENCES departments(id),
    officer_id     INTEGER REFERENCES users(id),
    assigned_by_id INTEGER REFERENCES users(id),
    note           TEXT,
    active         BOOLEAN DEFAULT TRUE,
    assigned_at    TIMESTAMP DEFAULT (now() AT TIME ZONE 'utc')
);

CREATE TABLE IF NOT EXISTS action_reports (
    id            SERIAL PRIMARY KEY,
    grievance_id  INTEGER NOT NULL REFERENCES grievances(id) ON DELETE CASCADE,
    officer_id    INTEGER NOT NULL REFERENCES users(id),
    report        TEXT NOT NULL,
    review_status VARCHAR(20) DEFAULT 'Pending'
                  CHECK (review_status IN ('Pending', 'Accepted', 'Returned')),
    cmo_remark    TEXT,
    created_at    TIMESTAMP DEFAULT (now() AT TIME ZONE 'utc'),
    reviewed_at   TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attachments (
    id             SERIAL PRIMARY KEY,
    grievance_id   INTEGER NOT NULL REFERENCES grievances(id) ON DELETE CASCADE,
    report_id      INTEGER REFERENCES action_reports(id) ON DELETE CASCADE,
    filename       VARCHAR(255) NOT NULL,
    mimetype       VARCHAR(100),
    size           INTEGER,
    data           BYTEA NOT NULL,
    kind           VARCHAR(20) DEFAULT 'supporting' CHECK (kind IN ('supporting', 'atr')),
    uploaded_by_id INTEGER REFERENCES users(id),
    created_at     TIMESTAMP DEFAULT (now() AT TIME ZONE 'utc')
);

CREATE TABLE IF NOT EXISTS feedback (
    id           SERIAL PRIMARY KEY,
    grievance_id INTEGER NOT NULL UNIQUE REFERENCES grievances(id) ON DELETE CASCADE,
    citizen_id   INTEGER NOT NULL REFERENCES users(id),
    rating       INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment      TEXT,
    created_at   TIMESTAMP DEFAULT (now() AT TIME ZONE 'utc')
);

CREATE TABLE IF NOT EXISTS contact_enquiries (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(120) NOT NULL,
    email      VARCHAR(160) NOT NULL,
    subject    VARCHAR(200) NOT NULL,
    message    TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT (now() AT TIME ZONE 'utc')
);

-- Supabase exposes every table in the public schema through its REST API.
-- Our Flask backend connects directly as the table owner, so it is not affected
-- by row level security. Enabling RLS with no policies blocks anyone using the
-- public (anon) API key from reading or writing these tables.
ALTER TABLE departments       ENABLE ROW LEVEL SECURITY;
ALTER TABLE users             ENABLE ROW LEVEL SECURITY;
ALTER TABLE grievances        ENABLE ROW LEVEL SECURITY;
ALTER TABLE grievance_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE assignments       ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_reports    ENABLE ROW LEVEL SECURITY;
ALTER TABLE attachments       ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback          ENABLE ROW LEVEL SECURITY;
ALTER TABLE contact_enquiries ENABLE ROW LEVEL SECURITY;
