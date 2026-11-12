"""Grievance workflow rules. Every change goes through log_action(),
so the full lifecycle (who, what, when) is always stored in grievance_history."""
from datetime import timedelta

from .models import SLA_DAYS, GrievanceHistory, db, now

# Which status changes each role may make via the generic status endpoint.
# Forwarding, action-taken reports and ATR review have their own endpoints
# but follow the same flow:
#   Submitted -> Under Review (CMO reviews/forwards) -> In Progress (officer acts)
#   -> ATR submitted -> CMO accepts -> Resolved -> (citizen) Reopened -> Under Review ...
TRANSITIONS = {
    "cmo": {
        "Submitted": {"Under Review", "Resolved"},
        "Reopened": {"Under Review", "Resolved"},
        "Under Review": {"Resolved"},
        "In Progress": {"Under Review", "Resolved"},
    },
    "officer": {
        "Under Review": {"In Progress"},
        "In Progress": {"In Progress"},  # progress update without status change
    },
    "citizen": {
        "Resolved": {"Reopened"},
    },
}
REMARK_REQUIRED = {"Resolved", "Reopened"}


def due_date(priority, start=None):
    return (start or now()) + timedelta(days=SLA_DAYS.get(priority, 7))


def log_action(grievance, user, action, remark=None, to_status=None, internal=False):
    """Change status (optional) and write one history row."""
    from_status = grievance.status
    if to_status and to_status != grievance.status:
        grievance.status = to_status
        if to_status == "Resolved":
            grievance.resolved_at = now()
        if to_status == "Reopened":
            grievance.resolved_at = None
            grievance.due_at = due_date(grievance.priority)
    grievance.updated_at = now()
    entry = GrievanceHistory(
        grievance=grievance, user=user, action=action, remark=remark,
        from_status=from_status, to_status=grievance.status, is_internal=internal,
    )
    db.session.add(entry)
    return entry


def can_transition(role, current, target):
    return target in TRANSITIONS.get(role, {}).get(current, set())


def can_view(user, grievance):
    if user.role == "cmo":
        return True
    if user.role == "citizen":
        return grievance.citizen_id == user.id
    if user.role == "officer":
        return grievance.department_id is not None and grievance.department_id == user.department_id
    return False
