"""Database models (tables). SQLAlchemy maps each class to one table."""
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

# Fixed lists used across the app
ROLES = ("citizen", "cmo", "officer")
STATUSES = ("Submitted", "Under Review", "In Progress", "Resolved", "Reopened")
PRIORITIES = ("Low", "Medium", "High")
CATEGORIES = (
    "Roads & Infrastructure", "Water Supply", "Electricity", "Healthcare",
    "Education", "Revenue & Land", "Police & Safety", "Social Welfare",
    "Sanitation & Waste", "Public Transport", "Agriculture", "Other",
)
DISTRICTS = (
    "Thiruvananthapuram", "Kollam", "Pathanamthitta", "Alappuzha", "Kottayam",
    "Idukki", "Ernakulam", "Thrissur", "Palakkad", "Malappuram", "Kozhikode",
    "Wayanad", "Kannur", "Kasaragod",
)
# Days allowed before a grievance counts as overdue
SLA_DAYS = {"High": 3, "Medium": 7, "Low": 14}


def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)  # stored as UTC


def iso(dt):
    return dt.isoformat() + "Z" if dt else None


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    mobile = db.Column(db.String(15))
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="citizen")
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))  # officers only
    created_at = db.Column(db.DateTime, default=now)

    department = db.relationship("Department")

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "email": self.email,
            "mobile": self.mobile, "role": self.role,
            "department_id": self.department_id,
            "department": self.department.name if self.department else None,
        }


class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "code": self.code,
                "description": self.description}


class Grievance(db.Model):
    __tablename__ = "grievances"
    id = db.Column(db.Integer, primary_key=True)
    ref_id = db.Column(db.String(30), unique=True, index=True)  # e.g. CMK-2026-000123
    citizen_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    district = db.Column(db.String(40), nullable=False)
    category = db.Column(db.String(60), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(10), default="Medium")
    status = db.Column(db.String(20), default="Submitted", index=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    escalated = db.Column(db.Boolean, default=False)
    due_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=now)
    updated_at = db.Column(db.DateTime, default=now, onupdate=now)
    resolved_at = db.Column(db.DateTime)

    # AI suggestions are stored separately from the official values,
    # so a reviewer can always see what the AI suggested vs. what a human decided.
    ai_department = db.Column(db.String(120))
    ai_category = db.Column(db.String(60))
    ai_priority = db.Column(db.String(10))
    ai_summary = db.Column(db.Text)
    ai_duplicate_ref = db.Column(db.String(30))
    ai_duplicate_reason = db.Column(db.Text)
    ai_source = db.Column(db.String(40))  # e.g. "gemini:gemini-3.8-flash" or "fallback"

    citizen = db.relationship("User", foreign_keys=[citizen_id])
    department = db.relationship("Department")
    history = db.relationship("GrievanceHistory", backref="grievance",
                              order_by="GrievanceHistory.created_at",
                              cascade="all, delete-orphan")
    attachments = db.relationship("Attachment", backref="grievance",
                                  cascade="all, delete-orphan")
    assignments = db.relationship("Assignment", backref="grievance",
                                  order_by="Assignment.assigned_at",
                                  cascade="all, delete-orphan")
    reports = db.relationship("ActionReport", backref="grievance",
                              order_by="ActionReport.created_at",
                              cascade="all, delete-orphan")
    feedback = db.relationship("Feedback", backref="grievance", uselist=False,
                               cascade="all, delete-orphan")

    @property
    def is_overdue(self):
        return self.status != "Resolved" and self.due_at is not None and now() > self.due_at

    @property
    def active_assignment(self):
        active = [a for a in self.assignments if a.active]
        return active[-1] if active else None

    def to_summary(self):
        a = self.active_assignment
        return {
            "id": self.id, "ref_id": self.ref_id, "subject": self.subject,
            "district": self.district, "category": self.category,
            "priority": self.priority, "status": self.status,
            "department": self.department.name if self.department else None,
            "officer": a.officer.name if a and a.officer else None,
            "escalated": self.escalated, "overdue": self.is_overdue,
            "citizen": self.citizen.name if self.citizen else None,
            "created_at": iso(self.created_at), "updated_at": iso(self.updated_at),
            "due_at": iso(self.due_at),
        }

    def to_detail(self, viewer_role):
        """Full record. Internal CMO remarks are hidden from citizens."""
        data = self.to_summary()
        data.update({
            "description": self.description,
            "department_id": self.department_id,
            "resolved_at": iso(self.resolved_at),
            "attachments": [x.to_dict() for x in self.attachments],
            "history": [h.to_dict() for h in self.history
                        if viewer_role != "citizen" or not h.is_internal],
            "reports": [r.to_dict() for r in self.reports],
            "feedback": self.feedback.to_dict() if self.feedback else None,
            "citizen_contact": ({"email": self.citizen.email, "mobile": self.citizen.mobile}
                                if viewer_role != "citizen" else None),
        })
        if viewer_role != "citizen":
            data["assignments"] = [x.to_dict() for x in self.assignments]
        data["ai"] = {
            "department": self.ai_department, "category": self.ai_category,
            "priority": self.ai_priority, "summary": self.ai_summary,
            "duplicate_ref": self.ai_duplicate_ref,
            "duplicate_reason": self.ai_duplicate_reason, "source": self.ai_source,
        }
        return data


class GrievanceHistory(db.Model):
    """One row per action / status change: who did what, and when."""
    __tablename__ = "grievance_history"
    id = db.Column(db.Integer, primary_key=True)
    grievance_id = db.Column(db.Integer, db.ForeignKey("grievances.id"), nullable=False, index=True)
    from_status = db.Column(db.String(20))
    to_status = db.Column(db.String(20))
    action = db.Column(db.String(60), nullable=False)
    remark = db.Column(db.Text)
    is_internal = db.Column(db.Boolean, default=False)  # hidden from citizen
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=now)

    user = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id, "from_status": self.from_status, "to_status": self.to_status,
            "action": self.action, "remark": self.remark, "is_internal": self.is_internal,
            "by": self.user.name if self.user else "System",
            "by_role": self.user.role if self.user else "system",
            "at": iso(self.created_at),
        }


class Assignment(db.Model):
    """Record of the CMO forwarding a grievance to a department/officer."""
    __tablename__ = "assignments"
    id = db.Column(db.Integer, primary_key=True)
    grievance_id = db.Column(db.Integer, db.ForeignKey("grievances.id"), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    officer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    assigned_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    note = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    assigned_at = db.Column(db.DateTime, default=now)

    department = db.relationship("Department")
    officer = db.relationship("User", foreign_keys=[officer_id])
    assigned_by = db.relationship("User", foreign_keys=[assigned_by_id])

    def to_dict(self):
        return {
            "id": self.id, "department": self.department.name,
            "officer": self.officer.name if self.officer else None,
            "assigned_by": self.assigned_by.name if self.assigned_by else None,
            "note": self.note, "active": self.active, "assigned_at": iso(self.assigned_at),
        }


class Attachment(db.Model):
    """Uploaded file. Bytes are stored in the DB so they persist on free hosting."""
    __tablename__ = "attachments"
    id = db.Column(db.Integer, primary_key=True)
    grievance_id = db.Column(db.Integer, db.ForeignKey("grievances.id"), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey("action_reports.id"))
    filename = db.Column(db.String(255), nullable=False)
    mimetype = db.Column(db.String(100))
    size = db.Column(db.Integer)
    data = db.Column(db.LargeBinary, nullable=False)
    kind = db.Column(db.String(20), default="supporting")  # supporting | atr
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=now)

    def to_dict(self):
        return {"id": self.id, "filename": self.filename, "mimetype": self.mimetype,
                "size": self.size, "kind": self.kind, "uploaded_at": iso(self.created_at)}


class ActionReport(db.Model):
    """Action-taken report (ATR) submitted by a department officer."""
    __tablename__ = "action_reports"
    id = db.Column(db.Integer, primary_key=True)
    grievance_id = db.Column(db.Integer, db.ForeignKey("grievances.id"), nullable=False)
    officer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    report = db.Column(db.Text, nullable=False)
    review_status = db.Column(db.String(20), default="Pending")  # Pending | Accepted | Returned
    cmo_remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=now)
    reviewed_at = db.Column(db.DateTime)

    officer = db.relationship("User")
    files = db.relationship("Attachment")

    def to_dict(self):
        return {
            "id": self.id, "officer": self.officer.name, "report": self.report,
            "review_status": self.review_status, "cmo_remark": self.cmo_remark,
            "created_at": iso(self.created_at), "reviewed_at": iso(self.reviewed_at),
            "files": [f.to_dict() for f in self.files],
        }


class Feedback(db.Model):
    __tablename__ = "feedback"
    id = db.Column(db.Integer, primary_key=True)
    grievance_id = db.Column(db.Integer, db.ForeignKey("grievances.id"), unique=True, nullable=False)
    citizen_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=now)

    def to_dict(self):
        return {"rating": self.rating, "comment": self.comment, "at": iso(self.created_at)}


class ContactEnquiry(db.Model):
    __tablename__ = "contact_enquiries"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=now)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email,
                "subject": self.subject, "message": self.message,
                "created_at": iso(self.created_at)}
