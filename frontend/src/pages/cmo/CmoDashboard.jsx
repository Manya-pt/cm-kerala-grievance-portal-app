// Chief Minister's Office dashboard: statistics, charts and filterable grievance list.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, Pie, PieChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import api, { errorMessage } from "../../api";
import { Alert, GrievanceTable, Loader, StatCard } from "../../components/UI";

const STATUS_COLORS = {
  Submitted: "#64748b", "Under Review": "#2563eb", "In Progress": "#d97706",
  Resolved: "#16a34a", Reopened: "#dc2626",
};
const EMPTY_FILTERS = { district: "", category: "", priority: "", status: "", department_id: "", overdue: "", q: "" };

export default function CmoDashboard() {
  const [stats, setStats] = useState(null);
  const [meta, setMeta] = useState({ districts: [], categories: [], priorities: [], statuses: [] });
  const [departments, setDepartments] = useState([]);
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/stats").then((r) => setStats(r.data)).catch((e) => setError(errorMessage(e)));
    api.get("/meta").then((r) => setMeta(r.data));
    api.get("/departments").then((r) => setDepartments(r.data));
  }, []);

  useEffect(() => {
    const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v));
    setItems(null);
    api.get("/grievances", { params }).then((r) => setItems(r.data)).catch((e) => setError(errorMessage(e)));
  }, [filters]);

  const set = (k) => (e) => setFilters({ ...filters, [k]: e.target.value });
  const quick = (patch) => setFilters({ ...EMPTY_FILTERS, ...patch });

  const statusData = stats ? Object.entries(stats.by_status).map(([name, value]) => ({ name, value })) : [];
  const districtData = stats?.by_district.filter((d) => d.total > 0) || [];
  const deptData = stats?.by_department.map((d) => ({ ...d, department: d.department.replace(" Department", "") })) || [];

  return (
    <div className="container section wide">
      <div className="section-head">
        <div>
          <h1>Chief Minister's Office dashboard</h1>
          <p className="muted">Review, forward and monitor all grievances across Kerala.</p>
        </div>
        <Link to="/cmo/enquiries" className="btn btn-outline">Contact enquiries</Link>
      </div>
      <Alert>{error}</Alert>
      {!stats ? <Loader /> : (
        <>
          <div className="stat-grid">
            <button className="stat-btn" onClick={() => quick({})}><StatCard label="Total grievances" value={stats.total} /></button>
            <button className="stat-btn" onClick={() => quick({ status: "Submitted" })}><StatCard label="Pending" value={stats.pending} tone="amber" hint={`${stats.by_status.Submitted || 0} new`} /></button>
            <button className="stat-btn" onClick={() => quick({ status: "Resolved" })}><StatCard label="Resolved" value={stats.resolved} tone="green" hint={stats.avg_resolution_days ? `avg ${stats.avg_resolution_days} days` : ""} /></button>
            <button className="stat-btn" onClick={() => quick({ overdue: "true" })}><StatCard label="Overdue" value={stats.overdue} tone="red" hint={`${stats.escalated} escalated`} /></button>
            <button className="stat-btn" onClick={() => quick({ status: "In Progress" })}><StatCard label="Reports to review" value={stats.awaiting_atr_review} tone="blue" /></button>
          </div>

          <div className="chart-grid">
            <div className="card">
              <h3>By status</h3>
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie data={statusData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={85} paddingAngle={2}>
                    {statusData.map((s) => <Cell key={s.name} fill={STATUS_COLORS[s.name]} />)}
                  </Pie>
                  <Tooltip /><Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="card">
              <h3>District-wise grievances</h3>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={districtData} margin={{ bottom: 40 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="district" angle={-35} textAnchor="end" interval={0} fontSize={11} />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="total" name="Total" fill="#0b5d3b" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="resolved" name="Resolved" fill="#f2b632" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="card">
              <h3>Department performance</h3>
              <ResponsiveContainer width="100%" height={340}>
                <BarChart data={deptData} layout="vertical" margin={{ left: 30 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" allowDecimals={false} />
                  <YAxis type="category" dataKey="department" width={130} fontSize={11} interval={0} />
                  <Tooltip /><Legend />
                  <Bar dataKey="resolved" stackId="a" name="Resolved" fill="#16a34a" />
                  <Bar dataKey="pending" stackId="a" name="Pending" fill="#d97706" />
                  <Bar dataKey="overdue" name="Overdue" fill="#dc2626" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="card">
              <h3>Monthly trend</h3>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={stats.trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" fontSize={11} />
                  <YAxis allowDecimals={false} />
                  <Tooltip /><Legend />
                  <Line type="monotone" dataKey="submitted" name="Submitted" stroke="#2563eb" strokeWidth={2} />
                  <Line type="monotone" dataKey="resolved" name="Resolved" stroke="#16a34a" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card">
            <h3>Department-wise summary</h3>
            <div className="table-wrap">
              <table className="table compact">
                <thead><tr><th>Department</th><th>Total</th><th>Resolved</th><th>Pending</th><th>Overdue</th><th>Resolution rate</th></tr></thead>
                <tbody>
                  {stats.by_department.map((d) => (
                    <tr key={d.department}>
                      <td>{d.department}</td><td>{d.total}</td><td>{d.resolved}</td><td>{d.pending}</td>
                      <td className={d.overdue ? "text-red" : ""}>{d.overdue}</td>
                      <td>{d.total ? Math.round((d.resolved / d.total) * 100) : 0}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      <div className="card">
        <h2>All grievances</h2>
        <div className="filters">
          <input placeholder="Search subject or reference" value={filters.q} onChange={set("q")} />
          <select value={filters.district} onChange={set("district")}><option value="">All districts</option>{meta.districts.map((d) => <option key={d}>{d}</option>)}</select>
          <select value={filters.category} onChange={set("category")}><option value="">All categories</option>{meta.categories.map((d) => <option key={d}>{d}</option>)}</select>
          <select value={filters.priority} onChange={set("priority")}><option value="">All priorities</option>{meta.priorities.map((d) => <option key={d}>{d}</option>)}</select>
          <select value={filters.status} onChange={set("status")}><option value="">All statuses</option>{meta.statuses.map((d) => <option key={d}>{d}</option>)}</select>
          <select value={filters.department_id} onChange={set("department_id")}><option value="">All departments</option>{departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}</select>
          <label className="checkbox"><input type="checkbox" checked={filters.overdue === "true"} onChange={(e) => setFilters({ ...filters, overdue: e.target.checked ? "true" : "" })} /> Overdue only</label>
          <button className="btn btn-outline btn-sm" onClick={() => setFilters(EMPTY_FILTERS)}>Clear</button>
        </div>
        {!items ? <Loader /> : <><p className="muted">{items.length} grievance(s)</p><GrievanceTable items={items} showCitizen /></>}
      </div>
    </div>
  );
}
