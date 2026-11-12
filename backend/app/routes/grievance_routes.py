"""Grievance endpoints: submit, list, detail, status, forward, remarks,
escalation, action-taken reports, feedback and file download."""
import io

from flask import Blueprint, current_app, g, jsonify, request, send_file
from werkzeug.utils import secure_filename

from ..ai_service import analyze_grievance
from ..auth import login_required
from ..models import (CATEGORIES, DISTRICTS, PRIORITIES, STATUSES, ActionReport,
                      Assignment, Attachment, Department, Feedback, Grievance, User, db, now)
from ..workflow import REMARK_REQUIRED, can_transition, can_view, due_date, log_action

bp = Blueprint("grievances", __name__, url_prefix="/api/grievances")


# ---------- helpers ----------
def _get_visible(gid):
    grievance = db.session.get(Grievance, gid)
    if grievance is None or not can_view(g.user, grievance):
        # same 404 for "missing" and "not yours" so IDs can't be probed
        return None, (jsonify(error="Grievance not found"), 404)
    return grievance, None


def _read_upload(field, grievance, kind, report=None):
    """Validate and store an uploaded file. Returns (attachment, error_message)."""
    file = request.files.get(field)
    if not file or not file.filename:
        return None, None
    name = secure_filename(file.filename)
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
        return None, "Only PNG, JPG and PDF files are allowed"
    data = file.read()
    # check the file really is what its extension says (magic bytes)
    if ext == "pdf" and not data.startswith(b"%PDF"):
        return None, "File content is not a valid PDF"
    if ext == "png" and not data.startswith(b"\x89PNG"):
        return None, "File content is not a valid PNG"
    if ext in ("jpg", "jpeg") and not data.startswith(b"\xff\xd8"):
        return None, "File content is not a valid JPG"
    mimetype = {"pdf": "application/pdf", "png": "image/png"}.get(ext, "image/jpeg")
    att = Attachment(grievance=grievance, filename=name, mimetype=mimetype, size=len(data),
                     data=data, kind=kind, uploaded_by_id=g.user.id,
                     report_id=report.id if report else None)
    db.session.add(att)
    return att, None


def _apply_ai(grievance, result):
    grievance.ai_department = result.get("department")
    grievance.ai_category = result.get("category")
    grievance.ai_priority = result.get("priority")
    grievance.ai_summary = result.get("summary")
    grievance.ai_duplicate_ref = result.get("duplicate_ref")
    grievance.ai_duplicate_reason = result.get("duplicate_reason")
    grievance.ai_source = (result.get("source") or "")[:40]


# ---------- citizen: submit ----------
@bp.post("")
@login_required("citizen")
def create():
    """multipart/form-data: district, category, subject, description, priority(optional), attachment(optional)"""
    f = request.form
    district, category = f.get("district", ""), f.get("category", "")
    subject, description = f.get("subject", "").strip(), f.get("description", "").strip()
    errors = {}
    if district not in DISTRICTS:
        errors["district"] = "Select a district"
    if category not in CATEGORIES:
        errors["category"] = "Select a category"
    if not 5 <= len(subject) <= 200:
        errors["subject"] = "Subject must be 5-200 characters"
    if len(description) < 20:
        errors["description"] = "Please describe the issue in at least 20 characters"
    if errors:
        return jsonify(error="Validation failed", fields=errors), 400

    # Citizen may accept the AI-suggested priority; otherwise Medium. CMO can change it later.
    priority = f.get("priority") if f.get("priority") in PRIORITIES else "Medium"
    grievance = Grievance(citizen_id=g.user.id, district=district, category=category,
                          subject=subject, description=description, priority=priority,
                          status="Submitted", due_at=due_date(priority))
    db.session.add(grievance)
    db.session.flush()  # gives us grievance.id
    grievance.ref_id = f"CMK-{grievance.created_at.year}-{grievance.id:06d}"

    att, err = _read_upload("attachment", grievance, "supporting")
    if err:
        db.session.rollback()
        return jsonify(error=err, fields={"attachment": err}), 400

    # Server-side AI analysis is stored with the record for the CMO (suggestion only).
    _apply_ai(grievance, analyze_grievance(f"{subject}. {description}", district,
                                           exclude_id=grievance.id))
    log_action(grievance, g.user, "Grievance submitted",
               remark=f"Reference number {grievance.ref_id} generated.", to_status="Submitted")
    db.session.commit()
    return jsonify(message="Grievance submitted successfully", ref_id=grievance.ref_id,
                   grievance=grievance.to_detail("citizen")), 201


# ---------- list ----------
@bp.get("")
@login_required()
def list_grievances():
    """Citizens see their own; officers see their department's; CMO sees all.
    Filters: district, category, priority, status, department_id, overdue=true, escalated=true, q"""
    q = Grievance.query
    if g.user.role == "citizen":
        q = q.filter(Grievance.citizen_id == g.user.id)
    elif g.user.role == "officer":
        q = q.filter(Grievance.department_id == g.user.department_id)

    args = request.args
    for field in ("district", "category", "priority", "status"):
        if args.get(field):
            q = q.filter(getattr(Grievance, field) == args[field])
    if args.get("department_id"):
        q = q.filter(Grievance.department_id == int(args["department_id"]))
    if args.get("escalated") == "true":
        q = q.filter(Grievance.escalated.is_(True))
    if args.get("q"):
        like = f"%{args['q']}%"
        q = q.filter(db.or_(Grievance.subject.ilike(like), Grievance.ref_id.ilike(like)))

    items = q.order_by(Grievance.created_at.desc()).limit(500).all()
    if args.get("overdue") == "true":
        items = [x for x in items if x.is_overdue]
    return jsonify([x.to_summary() for x in items])


# ---------- detail ----------
@bp.get("/<int:gid>")
@login_required()
def detail(gid):
    grievance, err = _get_visible(gid)
    if err:
        return err
    return jsonify(grievance.to_detail(g.user.role))


# ---------- generic status update ----------
@bp.patch("/<int:gid>/status")
@login_required()
def update_status(gid):
    grievance, err = _get_visible(gid)
    if err:
        return err
    data = request.get_json(silent=True) or {}
    target, remark = data.get("status"), (data.get("remark") or "").strip()
    if target not in STATUSES:
        return jsonify(error="Invalid status"), 400
    if not can_transition(g.user.role, grievance.status, target):
        return jsonify(error=f"A {g.user.role} cannot change status from "
                             f"'{grievance.status}' to '{target}'"), 409
    if target in REMARK_REQUIRED and not remark:
        return jsonify(error="A remark is required for this status"), 400
    if target == "Reopened" and grievance.citizen_id != g.user.id:
        return jsonify(error="Only the citizen can reopen"), 403

    action = {"Under Review": "Taken up for review by CMO", "In Progress": "Progress update",
              "Resolved": "Marked resolved", "Reopened": "Reopened by citizen"}[target]
    if target == "In Progress" and grievance.status == "Under Review":
        action = "Investigation started by department"
    log_action(grievance, g.user, action, remark=remark or None, to_status=target)
    db.session.commit()
    return jsonify(grievance.to_detail(g.user.role))


# ---------- CMO actions ----------
@bp.patch("/<int:gid>")
@login_required("cmo")
def edit(gid):
    """CMO may set official priority/category (e.g. accept the AI suggestion)."""
    grievance, err = _get_visible(gid)
    if err:
        return err
    data = request.get_json(silent=True) or {}
    changes = []
    if data.get("priority") in PRIORITIES and data["priority"] != grievance.priority:
        changes.append(f"Priority {grievance.priority} → {data['priority']}")
        grievance.priority = data["priority"]
        grievance.due_at = due_date(grievance.priority, grievance.created_at)
    if data.get("category") in CATEGORIES and data["category"] != grievance.category:
        changes.append(f"Category {grievance.category} → {data['category']}")
        grievance.category = data["category"]
    if not changes:
        return jsonify(error="No changes"), 400
    log_action(grievance, g.user, "Details updated by CMO", remark="; ".join(changes), internal=True)
    db.session.commit()
    return jsonify(grievance.to_detail("cmo"))


@bp.post("/<int:gid>/assign")
@login_required("cmo")
def assign(gid):
    """Forward to a department (and optionally a specific officer)."""
    grievance, err = _get_visible(gid)
    if err:
        return err
    data = request.get_json(silent=True) or {}
    dept = db.session.get(Department, int(data.get("department_id") or 0))
    if not dept:
        return jsonify(error="Select a valid department"), 400
    officer = None
    if data.get("officer_id"):
        officer = db.session.get(User, int(data["officer_id"]))
        if not officer or officer.role != "officer" or officer.department_id != dept.id:
            return jsonify(error="Officer does not belong to this department"), 400
    if grievance.status == "Resolved":
        return jsonify(error="Grievance is already resolved"), 409

    for a in grievance.assignments:
        a.active = False
    db.session.add(Assignment(grievance=grievance, department=dept, officer=officer,
                              assigned_by=g.user, note=data.get("note")))
    grievance.department_id = dept.id
    target = "Under Review" if grievance.status in ("Submitted", "Reopened") else grievance.status
    log_action(grievance, g.user, f"Forwarded to {dept.name}",
               remark=(data.get("note") or None), to_status=target)
    db.session.commit()
    return jsonify(grievance.to_detail("cmo"))


@bp.post("/<int:gid>/remarks")
@login_required("cmo", "officer")
def add_remark(gid):
    grievance, err = _get_visible(gid)
    if err:
        return err
    data = request.get_json(silent=True) or {}
    remark = (data.get("remark") or "").strip()
    if not remark:
        return jsonify(error="Remark cannot be empty"), 400
    internal = bool(data.get("internal"))
    label = "Internal remark" if internal else (
        "Remark from CMO" if g.user.role == "cmo" else "Remark from department officer")
    log_action(grievance, g.user, label, remark=remark[:2000], internal=internal)
    db.session.commit()
    return jsonify(grievance.to_detail(g.user.role))


@bp.post("/<int:gid>/escalate")
@login_required("cmo")
def escalate(gid):
    grievance, err = _get_visible(gid)
    if err:
        return err
    data = request.get_json(silent=True) or {}
    if grievance.status == "Resolved":
        return jsonify(error="Resolved grievances cannot be escalated"), 409
    grievance.escalated = True
    grievance.priority = "High"
    log_action(grievance, g.user, "Escalated by CMO",
               remark=(data.get("remark") or "Delayed grievance escalated for urgent action."))
    db.session.commit()
    return jsonify(grievance.to_detail("cmo"))


@bp.post("/<int:gid>/reanalyze")
@login_required("cmo")
def reanalyze(gid):
    grievance, err = _get_visible(gid)
    if err:
        return err
    result = analyze_grievance(f"{grievance.subject}. {grievance.description}",
                               grievance.district, exclude_id=grievance.id)
    _apply_ai(grievance, result)
    db.session.commit()
    return jsonify(grievance=grievance.to_detail("cmo"), ai=result)


@bp.post("/<int:gid>/reports/<int:rid>/review")
@login_required("cmo")
def review_report(gid, rid):
    """CMO accepts the action-taken report (→ Resolved) or returns it (→ In Progress)."""
    grievance, err = _get_visible(gid)
    if err:
        return err
    report = db.session.get(ActionReport, rid)
    if not report or report.grievance_id != grievance.id:
        return jsonify(error="Report not found"), 404
    if report.review_status != "Pending":
        return jsonify(error="Report already reviewed"), 409
    data = request.get_json(silent=True) or {}
    decision, remark = data.get("decision"), (data.get("remark") or "").strip()
    if decision not in ("accept", "return") or not remark:
        return jsonify(error="Decision (accept/return) and a remark are required"), 400

    report.reviewed_at, report.cmo_remark = now(), remark
    if decision == "accept":
        report.review_status = "Accepted"
        log_action(grievance, g.user, "Action-taken report accepted. Grievance resolved",
                   remark=remark, to_status="Resolved")
    else:
        report.review_status = "Returned"
        log_action(grievance, g.user, "Action-taken report returned to department",
                   remark=remark, to_status="In Progress", internal=True)
    db.session.commit()
    return jsonify(grievance.to_detail("cmo"))


# ---------- officer: action-taken report ----------
@bp.post("/<int:gid>/reports")
@login_required("officer")
def submit_report(gid):
    """multipart/form-data: report (text), attachment (optional file)."""
    grievance, err = _get_visible(gid)
    if err:
        return err
    text = (request.form.get("report") or "").strip()
    if len(text) < 10:
        return jsonify(error="Describe the action taken (at least 10 characters)"), 400
    if grievance.status not in ("Under Review", "In Progress"):
        return jsonify(error=f"Cannot submit a report while status is '{grievance.status}'"), 409
    if any(r.review_status == "Pending" for r in grievance.reports):
        return jsonify(error="A report is already awaiting CMO review"), 409

    report = ActionReport(grievance=grievance, officer=g.user, report=text[:5000])
    db.session.add(report)
    db.session.flush()
    _, ferr = _read_upload("attachment", grievance, "atr", report)
    if ferr:
        db.session.rollback()
        return jsonify(error=ferr), 400
    log_action(grievance, g.user, "Action-taken report submitted to CMO",
               remark=text[:500], to_status="In Progress")
    db.session.commit()
    return jsonify(grievance.to_detail("officer")), 201


# ---------- citizen: feedback ----------
@bp.post("/<int:gid>/feedback")
@login_required("citizen")
def feedback(gid):
    grievance, err = _get_visible(gid)
    if err:
        return err
    if grievance.status != "Resolved":
        return jsonify(error="Feedback can be given only after resolution"), 409
    if grievance.feedback:
        return jsonify(error="Feedback already submitted"), 409
    data = request.get_json(silent=True) or {}
    try:
        rating = int(data.get("rating"))
    except (TypeError, ValueError):
        rating = 0
    if not 1 <= rating <= 5:
        return jsonify(error="Rating must be between 1 and 5"), 400
    db.session.add(Feedback(grievance=grievance, citizen_id=g.user.id, rating=rating,
                            comment=(data.get("comment") or "")[:1000]))
    log_action(grievance, g.user, "Citizen feedback submitted",
               remark=f"Rating {rating}/5. {data.get('comment') or ''}".strip())
    db.session.commit()
    return jsonify(grievance.to_detail("citizen")), 201


# ---------- files ----------
@bp.get("/attachments/<int:aid>")
@login_required()
def download(aid):
    att = db.session.get(Attachment, aid)
    if not att or not can_view(g.user, att.grievance):
        return jsonify(error="File not found"), 404
    return send_file(io.BytesIO(att.data), mimetype=att.mimetype,
                     download_name=att.filename, as_attachment=False)
