import { useEffect, useState } from "react";
import api, { errorMessage } from "../../api";
import { useAuth } from "../../AuthContext";
import { Alert, GrievanceTable, Loader, StatCard } from "../../components/UI";

const TABS = ["Active", "Resolved", "All"];

export default function OfficerDashboard() {
  const { user } = useAuth();
  const [items, setItems] = useState(null);
  const [stats, setStats] = useState(null);
  const [tab, setTab] = useState("Active");
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/grievances").then((r) => setItems(r.data)).catch((e) => setError(errorMessage(e)));
    api.get("/stats").then((r) => setStats(r.data)).catch(() => {});
  }, []);

  const shown = (items || []).filter((g) =>
    tab === "All" ? true : tab === "Resolved" ? g.status === "Resolved" : g.status !== "Resolved");

  return (
    <div className="container section">
      <h1>{user.department} · Officer dashboard</h1>
      <p className="muted">Grievances forwarded to your department by the Chief Minister's Office.</p>
      <Alert>{error}</Alert>
      {stats && (
        <div className="stat-grid">
          <StatCard label="Assigned to department" value={stats.total} />
          <StatCard label="Awaiting action" value={stats.by_status["Under Review"] || 0} tone="blue" />
          <StatCard label="In progress" value={stats.by_status["In Progress"] || 0} tone="amber" />
          <StatCard label="Overdue" value={stats.overdue} tone="red" />
          <StatCard label="Resolved" value={stats.resolved} tone="green" />
        </div>
      )}
      <div className="card">
        <div className="tabs">
          {TABS.map((t) => <button key={t} className={t === tab ? "active" : ""} onClick={() => setTab(t)}>{t}</button>)}
        </div>
        {!items ? <Loader /> : <GrievanceTable items={shown} showCitizen empty="No grievances in this list." />}
      </div>
    </div>
  );
}
