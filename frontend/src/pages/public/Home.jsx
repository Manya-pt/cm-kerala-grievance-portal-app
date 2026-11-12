import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api";
import { StatCard } from "../../components/UI";

export default function Home() {
  const [stats, setStats] = useState(null);
  const [departments, setDepartments] = useState([]);

  useEffect(() => {
    api.get("/public-stats").then((r) => setStats(r.data)).catch(() => {});
    api.get("/departments").then((r) => setDepartments(r.data.slice(0, 6))).catch(() => {});
  }, []);

  return (
    <>
      <section className="hero">
        <div className="container hero-inner">
          <div>
            <span className="eyebrow">Chief Minister's Public Grievance Redressal</span>
            <h1>Your voice, heard directly by the Chief Minister's Office</h1>
            <p className="lead">
              Report problems with roads, water, electricity, healthcare, education and other public
              services. Track every step until your grievance is resolved.
            </p>
            <div className="hero-actions">
              <Link to="/citizen/submit" className="btn btn-gold btn-lg">Submit Grievance</Link>
              <Link to="/track" className="btn btn-outline-light btn-lg">Track Grievance</Link>
            </div>
          </div>
          <div className="hero-card">
            <h3>How your grievance moves</h3>
            <ol className="mini-steps">
              <li>Submit online and get a reference number</li>
              <li>CMO reviews it with AI-assisted triage</li>
              <li>Forwarded to the right department</li>
              <li>Officer acts and reports back</li>
              <li>You get updates and give feedback</li>
            </ol>
          </div>
        </div>
      </section>

      <section className="container section">
        <h2 className="section-title">Portal at a glance <small>(sample data)</small></h2>
        <div className="stat-grid">
          <StatCard label="Grievances received" value={stats?.total} />
          <StatCard label="Resolved" value={stats?.resolved} tone="green" />
          <StatCard label="In progress" value={stats?.pending} tone="amber" />
          <StatCard label="Departments" value={stats?.departments} />
          <StatCard label="Districts covered" value={stats?.districts} />
        </div>
      </section>

      <section className="container section">
        <div className="section-head">
          <h2 className="section-title">Featured departments</h2>
          <Link to="/departments">View all →</Link>
        </div>
        <div className="card-grid">
          {departments.map((d) => (
            <div className="card" key={d.id}>
              <span className="dept-code">{d.code}</span>
              <h3>{d.name}</h3>
              <p className="muted">{d.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="container section">
        <div className="cta-band">
          <div>
            <h2>Have a problem with a public service?</h2>
            <p>Register in under a minute. Our AI assistant helps you pick the right department.</p>
          </div>
          <Link to="/register" className="btn btn-gold btn-lg">Create account</Link>
        </div>
      </section>
    </>
  );
}
