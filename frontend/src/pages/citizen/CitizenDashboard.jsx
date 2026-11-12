import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import api, { errorMessage } from "../../api";
import { useAuth } from "../../AuthContext";
import { Alert, GrievanceTable, Loader, StatCard } from "../../components/UI";

export default function CitizenDashboard() {
  const { user } = useAuth();
  const location = useLocation();
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");
  const newRef = location.state?.newRef;

  useEffect(() => {
    api.get("/grievances").then((r) => setItems(r.data)).catch((e) => setError(errorMessage(e)));
  }, []);

  const resolved = items?.filter((g) => g.status === "Resolved").length ?? 0;

  return (
    <div className="container section">
      <div className="section-head">
        <div>
          <h1>Welcome, {user.name}</h1>
          <p className="muted">Your grievances and their latest updates.</p>
        </div>
        <Link to="/citizen/submit" className="btn btn-primary">+ Submit new grievance</Link>
      </div>
      {newRef && (
        <Alert type="success">
          Grievance submitted successfully. Your reference number is <b>{newRef}</b>. Keep it to track your grievance.
        </Alert>
      )}
      <Alert>{error}</Alert>
      {!items ? <Loader /> : (
        <>
          <div className="stat-grid">
            <StatCard label="Total submitted" value={items.length} />
            <StatCard label="Pending" value={items.length - resolved} tone="amber" />
            <StatCard label="Resolved" value={resolved} tone="green" />
            <StatCard label="Reopened" value={items.filter((g) => g.status === "Reopened").length} tone="red" />
          </div>
          <div className="card">
            <h2>My grievances</h2>
            <GrievanceTable items={items} empty="You have not submitted any grievances yet." />
          </div>
        </>
      )}
    </div>
  );
}
