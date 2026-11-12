"""Fictional demo data. Runs automatically when the database has no users.
Run manually with:  python -m app.seed   (from the backend folder)"""
import random
from datetime import timedelta

from .models import (ActionReport, Assignment, ContactEnquiry, Department, Feedback,
                     Grievance, GrievanceHistory, User, db, now)
from .workflow import due_date

DEMO_PASSWORD = "Demo@1234"

DEPARTMENTS = [
    ("PWD", "Public Works Department", "Roads, bridges, public buildings and street infrastructure."),
    ("KWA", "Water Authority", "Drinking water supply, pipelines and water quality."),
    ("KSEB", "Electricity Board", "Power supply, transformers, outages and electrical safety."),
    ("HEALTH", "Health & Family Welfare", "Government hospitals, PHCs, medicines and public health."),
    ("EDU", "General Education", "Government schools, teachers, scholarships and facilities."),
    ("REV", "Revenue Department", "Land records, certificates, village offices and land tax."),
    ("HOME", "Home Department (Police)", "Law and order, police stations and public safety."),
    ("SJD", "Social Justice Department", "Welfare pensions, disability support and social security."),
    ("LSGD", "Local Self Government", "Panchayats, municipalities, sanitation and waste management."),
    ("TRANS", "Transport Department", "Public bus services, routes and transport safety."),
    ("AGRI", "Agriculture Department", "Farmer support, crop loss, subsidies and irrigation."),
]

# (district, category, dept_code, priority, subject, description, stage)
# stage: 0 submitted, 1 forwarded, 2 in progress, 3 ATR pending, 4 resolved, 5 reopened
SAMPLES = [
    ("Ernakulam", "Roads & Infrastructure", "PWD", "High", "Large potholes on Aluva–Perumbavoor road",
     "Several deep potholes near Thottumugham junction have caused two-wheeler accidents this week. Rain water fills them at night and they are not visible.", 2),
    ("Thiruvananthapuram", "Water Supply", "KWA", "High", "No drinking water supply for 6 days in Kazhakuttam ward",
     "Our ward has not received pipe water for six days. Around 200 families depend on this supply and are buying water at high cost.", 4),
    ("Kozhikode", "Electricity", "KSEB", "High", "Low-hanging live wire near school",
     "An electric line is hanging very low near the gate of the government LP school in Feroke. Children pass under it every day.", 4),
    ("Thrissur", "Healthcare", "HEALTH", "Medium", "Medicine shortage at taluk hospital pharmacy",
     "Diabetes and blood pressure medicines have been unavailable at the Chalakudy taluk hospital pharmacy for three weeks.", 3),
    ("Kollam", "Sanitation & Waste", "LSGD", "Medium", "Garbage not collected for two weeks",
     "Household waste has not been collected in Kadappakada area for two weeks. Stray dogs scatter it and there is a bad smell.", 1),
    ("Palakkad", "Agriculture", "AGRI", "Medium", "Crop loss compensation not received",
     "My paddy crop was damaged in the August floods. I applied for compensation at the Krishi Bhavan but have not received any amount.", 2),
    ("Malappuram", "Social Welfare", "SJD", "Medium", "Widow pension stopped without notice",
     "My mother's widow pension has not been credited for the last four months. No reason was given by the panchayat office.", 4),
    ("Kannur", "Public Transport", "TRANS", "Low", "Request for additional bus on Thalassery–Iritty route",
     "Morning buses on the Thalassery to Iritty route are extremely crowded. Students and workers request one more service at 8 AM.", 0),
    ("Kottayam", "Revenue & Land", "REV", "Medium", "Delay in issuing possession certificate",
     "I applied for a possession certificate at Ettumanoor village office two months ago. The application is still pending.", 5),
    ("Alappuzha", "Roads & Infrastructure", "PWD", "Medium", "Street lights not working on beach road",
     "Most street lights on Alappuzha beach road have not worked for a month, making it unsafe for walkers at night.", 4),
    ("Idukki", "Healthcare", "HEALTH", "High", "No doctor at primary health centre at night",
     "The PHC at Adimali has no doctor after 6 PM. Patients from tribal settlements have to travel 40 km during emergencies.", 1),
    ("Wayanad", "Education", "EDU", "Medium", "Damaged roof in government school classroom",
     "The roof of two classrooms at the government UP school in Meppadi leaks badly during rain. Classes are being disrupted.", 2),
    ("Kasaragod", "Water Supply", "KWA", "Medium", "Pipeline leak wasting water on main road",
     "A major pipeline is leaking near the new bus stand for ten days and water is flowing on the road.", 0),
    ("Pathanamthitta", "Police & Safety", "HOME", "Medium", "Frequent bike thefts near railway station",
     "There have been at least five bike thefts at the Thiruvalla railway station parking area this month. We request police patrolling.", 1),
    ("Ernakulam", "Sanitation & Waste", "LSGD", "High", "Overflowing drainage causing mosquito breeding",
     "The canal near Kaloor stadium is blocked with plastic waste. Stagnant water is causing mosquito breeding and fever cases.", 3),
    ("Thiruvananthapuram", "Electricity", "KSEB", "Medium", "Frequent power cuts in evening",
     "Our area in Nemom faces 3-4 power cuts every evening for the past two weeks without any notice.", 0),
    ("Thrissur", "Education", "EDU", "Low", "Scholarship amount not credited",
     "My pre-matric scholarship for last academic year has not been credited although the application was approved.", 4),
    ("Kozhikode", "Roads & Infrastructure", "PWD", "Medium", "Footpath broken near medical college",
     "The footpath slabs near Kozhikode medical college main gate are broken. Elderly patients find it difficult to walk.", 0),
    ("Kollam", "Water Supply", "KWA", "Medium", "Muddy water from public tap",
     "Water from the public tap in Karunagappally ward 12 is muddy and smells bad for the last week.", 2),
    ("Palakkad", "Social Welfare", "SJD", "Low", "Disability certificate camp request",
     "Many differently-abled persons in Ottapalam need certificates. We request a medical board camp in the taluk.", 0),
    ("Malappuram", "Public Transport", "TRANS", "Medium", "KSRTC bus skipping stop",
     "The KSRTC fast passenger buses do not stop at Kottakkal changuvetty stop even when passengers wait.", 4),
    ("Ernakulam", "Roads & Infrastructure", "PWD", "High", "Potholes on Aluva Perumbavoor road causing accidents",
     "Big potholes near Thottumugham on the Aluva to Perumbavoor road. Many bike riders have fallen. Please repair urgently.", 0),
]

CONTACTS = [
    ("Anjali Menon", "anjali@example.com", "Can NRIs submit grievances?", "I live abroad. Can I submit a grievance for my parents in Kottayam?"),
    ("Rahul Nair", "rahul@example.com", "Mobile app", "Is there a mobile app planned for this portal?"),
]


def _ai_for(dept_name, category, priority, subject):
    return dict(ai_department=dept_name, ai_category=category, ai_priority=priority,
                ai_summary=f"Citizen reports: {subject.lower()}. Requires review by {dept_name}.",
                ai_source="seed (sample data)")


def seed_if_empty():
    if User.query.first():
        return False
    seed()
    return True


def seed():
    rnd = random.Random(42)
    depts = {}
    for code, name, desc in DEPARTMENTS:
        d = Department(code=code, name=name, description=desc)
        db.session.add(d)
        depts[code] = d
    db.session.flush()

    def make_user(name, email, role, mobile, dept=None):
        u = User(name=name, email=email, role=role, mobile=mobile, department=dept)
        u.set_password(DEMO_PASSWORD)
        db.session.add(u)
        return u

    cmo = make_user("CMO Administrator", "cmo@demo.com", "cmo", "9000000001")
    officers = {code: make_user(f"{d.name} Officer", f"officer.{code.lower()}@demo.com",
                                "officer", f"90000001{i:02d}", d)
                for i, (code, d) in enumerate(depts.items())}
    citizens = [make_user("Arun Kumar (Demo Citizen)", "citizen@demo.com", "citizen", "9847000001"),
                make_user("Fathima Rahman (Demo Citizen)", "citizen2@demo.com", "citizen", "9847000002")]
    db.session.flush()

    for i, (district, category, code, priority, subject, desc, stage) in enumerate(SAMPLES):
        dept, officer = depts[code], officers[code]
        start = now() - timedelta(days=rnd.randint(0, 9) + stage, hours=rnd.randint(0, 20))
        g = Grievance(citizen=citizens[i % 2], district=district, category=category,
                      subject=subject, description=desc, priority=priority, status="Submitted",
                      created_at=start, due_at=due_date(priority, start),
                      **_ai_for(dept.name, category, priority, subject))
        db.session.add(g)
        db.session.flush()
        g.ref_id = f"CMK-{start.year}-{g.id:06d}"
        t = [start]

        def step(user, action, remark=None, to=None, internal=False, hours=None):
            t[0] = t[0] + timedelta(hours=hours or rnd.randint(4, 30))
            db.session.add(GrievanceHistory(grievance=g, user=user, action=action, remark=remark,
                                            from_status=g.status, to_status=to or g.status,
                                            is_internal=internal, created_at=t[0]))
            if to:
                g.status = to
            g.updated_at = t[0]

        db.session.add(GrievanceHistory(grievance=g, user=g.citizen, action="Grievance submitted",
                                        remark=f"Reference number {g.ref_id} generated.",
                                        to_status="Submitted", created_at=start))
        if stage >= 1:
            db.session.add(Assignment(grievance=g, department=dept, officer=officer,
                                      assigned_by=cmo, note="Please verify and act.",
                                      assigned_at=start + timedelta(hours=6)))
            g.department = dept
            step(cmo, f"Forwarded to {dept.name}", "Please verify and act.", to="Under Review", hours=6)
        if stage >= 2:
            step(officer, "Investigation started by department",
                 "Field inspection scheduled.", to="In Progress")
        if stage >= 3:
            rep = ActionReport(grievance=g, officer=officer, created_at=t[0] + timedelta(hours=20),
                               report="Site inspected. Work order issued and corrective action completed. Photos on file.")
            db.session.add(rep)
            step(officer, "Action-taken report submitted to CMO", rep.report, hours=20)
            if stage >= 4:
                rep.review_status, rep.cmo_remark = "Accepted", "Verified with department. Closing grievance."
                rep.reviewed_at = t[0] + timedelta(hours=10)
                step(cmo, "Action-taken report accepted. Grievance resolved",
                     "The issue has been resolved by the department. Thank you for your patience.",
                     to="Resolved", hours=10)
                g.resolved_at = t[0]
                if stage == 4 and i % 3 == 0:
                    db.session.add(Feedback(grievance=g, citizen_id=g.citizen_id,rating=rnd.choice([4, 5]),
                                            comment="Issue fixed quickly. Thank you.",
                                            created_at=t[0] + timedelta(hours=5)))
        if stage == 5:
            step(g.citizen, "Reopened by citizen",
                 "The certificate has still not been issued to me.", to="Reopened")
            g.resolved_at = None
            g.due_at = due_date(priority, t[0])

    # mark one high-priority case escalated, one duplicate flagged
    idukki = Grievance.query.filter_by(district="Idukki").first()
    if idukki:
        idukki.escalated = True
        db.session.add(GrievanceHistory(grievance=idukki, user=cmo, action="Escalated by CMO",
                                        remark="Delayed grievance escalated for urgent action.",
                                        from_status=idukki.status, to_status=idukki.status,
                                        created_at=idukki.updated_at + timedelta(hours=2)))
    db.session.flush()
    first, dup = Grievance.query.filter(Grievance.subject.ilike("%Perumbavoor%")).order_by(Grievance.id).all()[:2]
    dup.ai_duplicate_ref = first.ref_id
    dup.ai_duplicate_reason = "Same road and junction (Thottumugham) and the same pothole issue."

    for name, email, subject, msg in CONTACTS:
        db.session.add(ContactEnquiry(name=name, email=email, subject=subject, message=msg))
    db.session.commit()
    print(f"Seeded {len(SAMPLES)} grievances. Demo password for all accounts: {DEMO_PASSWORD}")


if __name__ == "__main__":
    from . import create_app
    from .config import Config

    class NoSeed(Config):
        SEED_ON_START = False

    app = create_app(NoSeed)
    with app.app_context():
        if not seed_if_empty():
            print("Database already has data. Nothing seeded.")
