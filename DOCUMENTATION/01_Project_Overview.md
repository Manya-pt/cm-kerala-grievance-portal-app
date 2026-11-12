# 01 – Project Overview

> Recruitment prototype. Not affiliated with the Government of Kerala. Fictional data only.

## Problem statement
Citizens across Kerala face problems with roads, water, electricity, healthcare, education and other public services. Complaints sent by letter, phone or in person are hard to track. Citizens don't know who is handling their issue, and the Chief Minister's Office (CMO) has no single view of pending, delayed or repeated complaints across departments and districts.

## Objectives
1. Give citizens one online channel to submit grievances directly to the CMO.
2. Give every grievance a unique reference number and a complete, timestamped history.
3. Let the CMO review, prioritise and forward grievances to the right department and officer.
4. Let department officers record investigation progress and submit action-taken reports.
5. Let the CMO verify reports before a grievance is resolved, and let citizens give feedback or reopen.
6. Use AI responsibly to speed up triage (department, category, priority, summary, duplicates) while keeping humans in control.
7. Give the CMO district-wise and department-wise statistics to monitor performance and delays.

## Scope
**In scope (prototype):** public website, citizen portal, CMO dashboard, department officer dashboard, the full grievance workflow, AI Grievance Assistant, file upload/retrieval, statistics and charts, documentation, deployment.

**Out of scope:** email/SMS notifications, real government integrations, Aadhaar/e-KYC, multilingual UI, admin screens for creating officers (done with seed data).

## Users and roles
| Role | Can do |
|---|---|
| Public visitor | Read information pages, view departments, send a contact enquiry, track a grievance by reference number |
| Citizen | Register/login, submit grievances with attachments, use the AI assistant, view the dashboard and history, give feedback, reopen |
| CMO administrator | See all grievances and statistics, filter, view attachments, forward, add remarks, escalate, change priority/category, review action-taken reports, resolve, view contact enquiries |
| Department officer | See grievances forwarded to their department, update status, add remarks, submit action-taken reports with files |

## Feature list
### Public website
Home (intro, Submit/Track buttons, live sample statistics, featured departments, footer) · About Us (purpose, vision, mission, objectives) · How It Works · Departments · Contact Us (saved in DB) · FAQ · Track grievance

### Citizen portal
Registration with name, email, mobile and password (validated) · login/logout · submit grievance (district, category, subject, description, optional priority, optional JPG/PNG/PDF) · AI suggestions · unique reference ID · citizen dashboard with total/pending/resolved/reopened counts · grievance detail with public remarks and status history · star rating feedback · reopen with reason

### CMO dashboard
Counts for total, pending, resolved, overdue and reports awaiting review · filters by district, category, priority, status, department, overdue and text search · charts by status, district, department and month · department summary table · grievance detail with attachments and AI analysis · forward to department/officer · internal or public remarks · escalate (sets High priority) · accept the AI priority/category · review action-taken reports · resolve directly · contact enquiries

### Department officer dashboard
Department-only grievance list (Active/Resolved/All) · counts · start investigation · progress updates · internal notes · action-taken report with optional file

### Workflow
`Submitted → Under Review → In Progress → (ATR) → Resolved → Reopened`, with every change stored with timestamp and responsible user. Grievances become **overdue** after 3/7/14 days for High/Medium/Low priority.

### AI
Department, category and priority suggestions, CMO summary, duplicate flagging, all reviewable and never applied automatically. See [05_AI_Integration.md](05_AI_Integration.md).
