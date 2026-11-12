import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { errorMessage, fieldErrors } from "../../api";
import { Alert, Loader } from "../../components/UI";

const EMPTY = { name: "", email: "", mobile: "", password: "", department_id: "" };

// CMO creates department officer accounts (officers cannot self-register).
export default function Officers() {
  const [officers, setOfficers] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const load = () => api.get("/officers").then((r) => setOfficers(r.data)).catch((e) => setError(errorMessage(e)));
  useEffect(() => {
    load();
    api.get("/departments").then((r) => setDepartments(r.data)).catch(() => {});
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setErrors({});
    setError("");
    setSuccess("");
    try {
      const { data } = await api.post("/officers", form);
      setSuccess(`Officer account created for ${data.email}. Share the password with them securely.`);
      setForm(EMPTY);
      load();
    } catch (err) {
      setErrors(fieldErrors(err));
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="container section">
      <Link to="/cmo">← Back to dashboard</Link>
      <h1>Department officers</h1>
      <Alert>{error}</Alert>
      {success && <div className="alert alert-success">{success}</div>}

      <div className="card" style={{ padding: 20, marginBottom: 20 }}>
        <h3>Create officer account</h3>
        <form onSubmit={submit} className="form">
          <label>Department
            <select value={form.department_id} onChange={set("department_id")} required>
              <option value="">Select department</option>
              {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
            {errors.department_id && <span className="field-error">{errors.department_id}</span>}
          </label>
          <label>Full name<input value={form.name} onChange={set("name")} required />{errors.name && <span className="field-error">{errors.name}</span>}</label>
          <label>Email<input type="email" value={form.email} onChange={set("email")} required />{errors.email && <span className="field-error">{errors.email}</span>}</label>
          <label>Mobile<input value={form.mobile} onChange={set("mobile")} placeholder="10-digit mobile" required />{errors.mobile && <span className="field-error">{errors.mobile}</span>}</label>
          <label>Initial password<input type="password" value={form.password} onChange={set("password")} required autoComplete="new-password" />
            <small className="muted">At least 8 characters with letters and numbers.</small>
            {errors.password && <span className="field-error">{errors.password}</span>}</label>
          <button className="btn btn-primary" disabled={busy}>{busy ? "Creating..." : "Create officer"}</button>
        </form>
      </div>

      {!officers ? <Loader /> : (
        <div className="card table-wrap">
          <table className="table">
            <thead><tr><th>Name</th><th>Department</th><th>Email</th><th>Mobile</th></tr></thead>
            <tbody>
              {officers.map((o) => (
                <tr key={o.id}><td>{o.name}</td><td>{o.department}</td><td>{o.email}</td><td>{o.mobile}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
