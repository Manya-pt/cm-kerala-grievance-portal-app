# 04 – API Documentation

**Base URL:** `https://<backend>.onrender.com/api` (local: `http://localhost:5000/api`)
**Format:** JSON (file uploads use `multipart/form-data`)
**Auth:** `Authorization: Bearer <JWT>` returned by login/register

**Error format:** `{ "error": "message", "fields": { "field": "message" } }` (`fields` only for validation errors)
**Status codes:** 200 OK · 201 Created · 400 Validation error · 401 Not logged in / bad token · 403 Wrong role · 404 Not found or not yours · 409 Not allowed in the current status · 500 Server error

## Required operations → endpoints
| Required operation | Endpoint |
|---|---|
| Citizen registration / login | `POST /auth/register`, `POST /auth/login` |
| Submit grievance | `POST /grievances` |
| Retrieve / list grievances | `GET /grievances`, `GET /grievances/{id}` |
| Track grievance by ID | `GET /track/{ref_id}` |
| Update grievance status | `PATCH /grievances/{id}/status` (+ assign, reports, review) |
| Retrieve departments | `GET /departments` |
| Retrieve CMO statistics | `GET /stats` |
| AI grievance analysis | `POST /ai/analyze`, `POST /grievances/{id}/reanalyze` |

## Endpoint summary
| Method | Path | Access | Description |
|---|---|---|---|
| GET | `/health` | Public | Health check |
| GET | `/meta` | Public | Districts, categories, priorities, statuses |
| GET | `/departments` | Public | List departments |
| GET | `/public-stats` | Public | Home page counts |
| POST | `/contact` | Public | Save a contact enquiry |
| GET | `/track/{ref_id}` | Public | Status, department and public history |
| POST | `/auth/register` | Public | Register citizen |
| POST | `/auth/login` | Public | Login (any role) |
| GET | `/auth/me` | Logged in | Current user |
| POST | `/auth/logout` | Logged in | Logout (client discards token) |
| POST | `/grievances` | Citizen | Submit grievance (multipart) |
| GET | `/grievances` | Logged in | List (scoped by role) with filters |
| GET | `/grievances/{id}` | Owner / dept officer / CMO | Full detail |
| PATCH | `/grievances/{id}/status` | Role-dependent | Change status (rules below) |
| PATCH | `/grievances/{id}` | CMO | Set official priority/category |
| POST | `/grievances/{id}/assign` | CMO | Forward to department/officer |
| POST | `/grievances/{id}/remarks` | CMO, Officer | Add remark (public or internal) |
| POST | `/grievances/{id}/escalate` | CMO | Escalate (priority → High) |
| POST | `/grievances/{id}/reanalyze` | CMO | Re-run AI analysis |
| POST | `/grievances/{id}/reports` | Officer | Submit action-taken report (multipart) |
| POST | `/grievances/{id}/reports/{rid}/review` | CMO | Accept or return ATR |
| POST | `/grievances/{id}/feedback` | Citizen (owner) | Rate after resolution |
| GET | `/grievances/attachments/{aid}` | Same as grievance | Download file |
| GET | `/stats` | CMO / Officer / Citizen | Dashboard statistics (scoped) |
| POST | `/ai/analyze` | Citizen, CMO | AI suggestions for a draft complaint |
| GET | `/officers?department_id=` | CMO | Officers list |
| GET | `/contact-enquiries` | CMO | Contact enquiries |

### Status transition rules (`PATCH /grievances/{id}/status`)
| Role | From | To |
|---|---|---|
| CMO | Submitted, Reopened | Under Review, Resolved |
| CMO | Under Review, In Progress | Resolved (In Progress → Under Review also allowed) |
| Officer (own dept) | Under Review | In Progress |
| Officer (own dept) | In Progress | In Progress (progress update) |
| Citizen (owner) | Resolved | Reopened |

`Resolved` and `Reopened` require a `remark`. Forwarding sets `Under Review`; an ATR sets `In Progress`; accepting an ATR sets `Resolved`; returning it sets `In Progress`.

---

## Examples

### POST /auth/register
```json
// request
{ "name": "Anu Thomas", "email": "anu@example.com", "mobile": "9876543210", "password": "Passw0rd1" }
// 201
{ "token": "eyJhbGciOi...", "user": { "id": 15, "name": "Anu Thomas", "email": "anu@example.com", "mobile": "9876543210", "role": "citizen", "department_id": null, "department": null } }
// 400
{ "error": "Validation failed", "fields": { "mobile": "Enter a valid 10-digit mobile number" } }
```

### POST /auth/login
```json
{ "email": "cmo@demo.com", "password": "Demo@1234" }
// 200 → { "token": "...", "user": { "role": "cmo", ... } }
// 401 → { "error": "Invalid email or password" }
```

### POST /grievances (citizen, multipart/form-data)
| Field | Required | Notes |
|---|---|---|
| district | yes | one of 14 districts |
| category | yes | from `/meta` |
| subject | yes | 5–200 chars |
| description | yes | ≥ 20 chars |
| priority | no | Low/Medium/High (default Medium) |
| attachment | no | JPG/PNG/PDF ≤ 5 MB, content verified |

```bash
curl -X POST $API/grievances -H "Authorization: Bearer $TOKEN" \
  -F district=Ernakulam -F category="Water Supply" \
  -F subject="No water supply for 4 days" \
  -F description="Our street in Kaloor has had no drinking water for four days." \
  -F attachment=@photo.jpg
```
```json
// 201
{
  "message": "Grievance submitted successfully",
  "ref_id": "CMK-2026-000023",
  "grievance": {
    "id": 23, "ref_id": "CMK-2026-000023", "status": "Submitted", "priority": "Medium",
    "district": "Ernakulam", "category": "Water Supply", "department": null,
    "attachments": [{ "id": 3, "filename": "photo.jpg", "mimetype": "image/jpeg", "size": 48211, "kind": "supporting" }],
    "history": [{ "action": "Grievance submitted", "to_status": "Submitted", "by": "Arun Kumar", "at": "2026-11-12T05:10:00Z" }],
    "ai": { "department": "Water Authority", "category": "Water Supply", "priority": "High",
            "summary": "Residents of a Kaloor street report no drinking water supply for four days.",
            "duplicate_ref": null, "source": "gemini:gemini-3.8-flash" }
  }
}
```

### GET /grievances
Query filters: `district`, `category`, `priority`, `status`, `department_id`, `overdue=true`, `escalated=true`, `q` (subject/reference search).
```json
[ { "id": 23, "ref_id": "CMK-2026-000023", "subject": "No water supply for 4 days", "district": "Ernakulam",
    "category": "Water Supply", "priority": "Medium", "status": "Submitted", "department": null,
    "officer": null, "escalated": false, "overdue": false, "citizen": "Arun Kumar",
    "created_at": "...", "updated_at": "...", "due_at": "..." } ]
```

### GET /track/{ref_id} (public)
```json
{ "ref_id": "CMK-2026-000002", "subject": "No drinking water supply for 6 days in Kazhakuttam ward",
  "status": "Resolved", "priority": "High", "department": "Water Authority", "district": "Thiruvananthapuram",
  "history": [ { "action": "Grievance submitted", "to_status": "Submitted", "remark": "...", "by_role": "citizen", "at": "..." },
               { "action": "Forwarded to Water Authority", "to_status": "Under Review", "by_role": "cmo", "at": "..." } ] }
```
Internal remarks and personal details are never included.

### PATCH /grievances/{id}/status
```json
{ "status": "In Progress", "remark": "Field team inspected the pipeline." }
// 409 → { "error": "A officer cannot change status from 'Submitted' to 'In Progress'" }
```

### POST /grievances/{id}/assign (CMO)
```json
{ "department_id": 2, "officer_id": 5, "note": "Restore supply within 48 hours." }
// 200 → full grievance, status "Under Review", new history row "Forwarded to Water Authority"
```

### POST /grievances/{id}/remarks
```json
{ "remark": "Contractor contacted.", "internal": true }
```

### POST /grievances/{id}/reports (officer, multipart)
Fields: `report` (text, ≥ 10 chars), `attachment` (optional file). Only one pending report at a time.

### POST /grievances/{id}/reports/{rid}/review (CMO)
```json
{ "decision": "accept", "remark": "Verified with photos. Closing." }   // → Resolved
{ "decision": "return", "remark": "Photos missing, please resubmit." }  // → In Progress
```

### POST /grievances/{id}/feedback (citizen)
```json
{ "rating": 5, "comment": "Fixed quickly." }
```

### GET /stats
```json
{ "total": 22, "pending": 16, "resolved": 6, "overdue": 9, "escalated": 1, "awaiting_atr_review": 2,
  "avg_resolution_days": 2.5,
  "by_status": { "Submitted": 7, "Under Review": 4, "In Progress": 4, "Resolved": 6, "Reopened": 1 },
  "by_priority": { "High": 7, "Medium": 12, "Low": 3 },
  "by_category": { "Water Supply": 3, "...": 0 },
  "by_department": [ { "department": "Water Authority", "total": 3, "resolved": 1, "pending": 2, "overdue": 0 } ],
  "by_district": [ { "district": "Ernakulam", "total": 4, "resolved": 0 } ],
  "trend": [ { "month": "2026-11", "submitted": 20, "resolved": 6 } ] }
```
CMO = all data; officer = own department; citizen = own grievances.

### POST /ai/analyze
```json
// request
{ "subject": "Live wire fallen", "description": "A live electric wire has fallen near Kaloor market.", "district": "Ernakulam" }
// 200
{ "department": "Electricity Board", "category": "Electricity", "priority": "High",
  "summary": "A live electric wire has fallen near Kaloor market, posing a safety risk.",
  "priority_reason": "Immediate risk to life.", "duplicate_ref": null, "duplicate_reason": null,
  "source": "gemini:gemini-3.8-flash", "notice": "AI suggestions only. Please review before accepting." }
```
If the AI is unavailable, `source` is `"fallback"` and `notice` says the output is not AI.

### POST /contact
```json
{ "name": "Rahul", "email": "rahul@example.com", "subject": "Mobile app", "message": "Is an app planned?" }
// 201 → { "message": "Thank you. Your enquiry has been received.", "id": 3 }
```
