// Small reusable UI pieces.
import { Link } from "react-router-dom";

export const formatDate = (iso, withTime = true) =>
  iso
    ? new Date(iso).toLocaleString("en-IN", {
        day: "2-digit", month: "short", year: "numeric",
        ...(withTime ? { hour: "2-digit", minute: "2-digit" } : {}),
      })
    : "—";

export const StatusBadge = ({ status }) => (
  <span className={`badge status-${status?.replace(" ", "-").toLowerCase()}`}>{status}</span>
);

export const PriorityBadge = ({ priority }) => (
  <span className={`badge priority-${priority?.toLowerCase()}`}>{priority}</span>
);

export const StatCard = ({ label, value, tone = "", hint }) => (
  <div className={`stat-card ${tone}`}>
    <div className="stat-value">{value ?? "—"}</div>
    <div className="stat-label">{label}</div>
    {hint && <div className="stat-hint">{hint}</div>}
  </div>
);

export const Loader = ({ text = "Loading..." }) => <div className="loader">{text}</div>;

export const Alert = ({ type = "error", children }) =>
  children ? <div className={`alert alert-${type}`}>{children}</div> : null;

export function GrievanceTable({ items, showCitizen = false, empty = "No grievances found." }) {
  if (!items.length) return <p className="muted">{empty}</p>;
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            <th>Reference</th>
            <th>Subject</th>
            <th>District</th>
            {showCitizen && <th>Citizen</th>}
            <th>Department</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Submitted</th>
          </tr>
        </thead>
        <tbody>
          {items.map((g) => (
            <tr key={g.id}>
              <td><Link to={`/grievances/${g.id}`} className="ref">{g.ref_id}</Link></td>
              <td>
                <Link to={`/grievances/${g.id}`}>{g.subject}</Link>
                <div className="tags">
                  {g.overdue && <span className="tag tag-red">Overdue</span>}
                  {g.escalated && <span className="tag tag-orange">Escalated</span>}
                </div>
              </td>
              <td>{g.district}</td>
              {showCitizen && <td>{g.citizen}</td>}
              <td>{g.department || <span className="muted">Unassigned</span>}</td>
              <td><PriorityBadge priority={g.priority} /></td>
              <td><StatusBadge status={g.status} /></td>
              <td className="nowrap">{formatDate(g.created_at, false)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Timeline({ history }) {
  return (
    <ol className="timeline">
      {history.map((h, i) => (
        <li key={h.id ?? i} className={h.is_internal ? "internal" : ""}>
          <div className="timeline-dot" />
          <div>
            <div className="timeline-head">
              <strong>{h.action}</strong>
              {h.to_status && h.from_status !== h.to_status && <StatusBadge status={h.to_status} />}
              {h.is_internal && <span className="tag tag-gray">Internal</span>}
            </div>
            {h.remark && <p className="timeline-remark">{h.remark}</p>}
            <small className="muted">
              {h.by ? `${h.by} (${h.by_role})` : h.by_role === "system" ? "System" : roleLabel(h.by_role)} · {formatDate(h.at)}
            </small>
          </div>
        </li>
      ))}
    </ol>
  );
}

const roleLabel = (r) => ({ cmo: "Chief Minister's Office", officer: "Department officer", citizen: "Citizen" })[r] || r;
