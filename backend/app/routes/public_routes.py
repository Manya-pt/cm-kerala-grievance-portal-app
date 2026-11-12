"""Public endpoints: departments, contact form, public tracking, home-page stats, lookups."""
import re

from flask import Blueprint, jsonify, request

from ..models import (CATEGORIES, DISTRICTS, PRIORITIES, STATUSES, ContactEnquiry,
                      Department, Grievance, db, iso)

bp = Blueprint("public", __name__, url_prefix="/api")


@bp.get("/health")
def health():
    return jsonify(status="ok")


@bp.get("/meta")
def meta():
    """Dropdown values used by the frontend."""
    return jsonify(districts=DISTRICTS, categories=CATEGORIES,
                   priorities=PRIORITIES, statuses=STATUSES)


@bp.get("/departments")
def departments():
    return jsonify([d.to_dict() for d in Department.query.order_by(Department.name)])


@bp.post("/contact")
def contact():
    data = request.get_json(silent=True) or {}
    fields = {k: (data.get(k) or "").strip() for k in ("name", "email", "subject", "message")}
    missing = [k for k, v in fields.items() if not v]
    if missing:
        return jsonify(error="All fields are required", fields={k: "Required" for k in missing}), 400
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", fields["email"]):
        return jsonify(error="Enter a valid email", fields={"email": "Invalid email"}), 400
    enquiry = ContactEnquiry(**{k: v[:2000] for k, v in fields.items()})
    db.session.add(enquiry)
    db.session.commit()
    return jsonify(message="Thank you. Your enquiry has been received.", id=enquiry.id), 201


@bp.get("/track/<ref_id>")
def track(ref_id):
    """Anyone with the reference number can see status, department and public history.
    No personal details or internal remarks are exposed."""
    g = Grievance.query.filter_by(ref_id=ref_id.strip().upper()).first()
    if not g:
        return jsonify(error="No grievance found with this reference number"), 404
    return jsonify(
        ref_id=g.ref_id, subject=g.subject, district=g.district, category=g.category,
        status=g.status, priority=g.priority,
        department=g.department.name if g.department else "Not yet assigned",
        created_at=iso(g.created_at), updated_at=iso(g.updated_at),
        history=[{"action": h.action, "to_status": h.to_status, "remark": h.remark,
                  "by_role": h.user.role if h.user else "system", "at": iso(h.created_at)}
                 for h in g.history if not h.is_internal],
    )


@bp.get("/public-stats")
def public_stats():
    total = Grievance.query.count()
    resolved = Grievance.query.filter_by(status="Resolved").count()
    return jsonify(total=total, resolved=resolved, pending=total - resolved,
                   departments=Department.query.count(), districts=len(DISTRICTS))
