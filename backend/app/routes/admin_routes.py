"""Statistics, AI analysis, officer list and contact enquiries."""
from collections import Counter, defaultdict
from datetime import timedelta

from flask import Blueprint, g, jsonify, request

from ..ai_service import analyze_grievance
from ..auth import login_required
from ..models import DISTRICTS, ContactEnquiry, Department, Grievance, User, now

bp = Blueprint("admin", __name__, url_prefix="/api")


@bp.get("/stats")
@login_required("cmo", "officer", "citizen")
def stats():
    """Dashboard statistics. CMO: whole state. Officer: own department. Citizen: own grievances."""
    q = Grievance.query
    if g.user.role == "officer":
        q = q.filter(Grievance.department_id == g.user.department_id)
    elif g.user.role == "citizen":
        q = q.filter(Grievance.citizen_id == g.user.id)
    items = q.all()

    resolved = [x for x in items if x.status == "Resolved"]
    durations = [(x.resolved_at - x.created_at).total_seconds() / 86400
                 for x in resolved if x.resolved_at]

    by_dept = defaultdict(lambda: {"total": 0, "resolved": 0, "pending": 0, "overdue": 0})
    for x in items:
        d = by_dept[x.department.name if x.department else "Unassigned"]
        d["total"] += 1
        d["resolved" if x.status == "Resolved" else "pending"] += 1
        d["overdue"] += int(x.is_overdue)

    by_district = {name: {"total": 0, "resolved": 0} for name in DISTRICTS}
    for x in items:
        by_district[x.district]["total"] += 1
        by_district[x.district]["resolved"] += int(x.status == "Resolved")

    # last 6 months trend
    months = []
    cursor = now().replace(day=1)
    for _ in range(6):
        months.append(cursor.strftime("%Y-%m"))
        cursor = (cursor - timedelta(days=1)).replace(day=1)
    months.reverse()
    created = Counter(x.created_at.strftime("%Y-%m") for x in items)
    closed = Counter(x.resolved_at.strftime("%Y-%m") for x in resolved if x.resolved_at)

    return jsonify(
        total=len(items),
        resolved=len(resolved),
        pending=len(items) - len(resolved),
        overdue=sum(x.is_overdue for x in items),
        escalated=sum(bool(x.escalated) and x.status != "Resolved" for x in items),
        awaiting_atr_review=sum(any(r.review_status == "Pending" for r in x.reports) for x in items),
        avg_resolution_days=round(sum(durations) / len(durations), 1) if durations else None,
        by_status=dict(Counter(x.status for x in items)),
        by_priority=dict(Counter(x.priority for x in items)),
        by_category=dict(Counter(x.category for x in items)),
        by_department=[{"department": k, **v} for k, v in sorted(by_dept.items())],
        by_district=[{"district": k, **v} for k, v in by_district.items()],
        trend=[{"month": m, "submitted": created.get(m, 0), "resolved": closed.get(m, 0)}
               for m in months],
    )


@bp.post("/ai/analyze")
@login_required("citizen", "cmo")
def ai_analyze():
    """Preview AI suggestions while the citizen is writing the complaint."""
    data = request.get_json(silent=True) or {}
    text = f"{data.get('subject', '')}. {data.get('description', '')}".strip(". ")
    if len(text) < 20:
        return jsonify(error="Write a little more about the issue first (at least 20 characters)"), 400
    return jsonify(analyze_grievance(text, data.get("district")))


@bp.get("/officers")
@login_required("cmo")
def officers():
    q = User.query.filter_by(role="officer")
    if request.args.get("department_id"):
        q = q.filter_by(department_id=int(request.args["department_id"]))
    return jsonify([u.to_dict() for u in q.order_by(User.name)])


@bp.get("/contact-enquiries")
@login_required("cmo")
def enquiries():
    rows = ContactEnquiry.query.order_by(ContactEnquiry.created_at.desc()).limit(200)
    return jsonify([r.to_dict() for r in rows])
