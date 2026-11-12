import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { errorMessage, fieldErrors } from "../../api";
import { useAuth } from "../../AuthContext";
import { Alert } from "../../components/UI";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", mobile: "", password: "" });
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setErrors({});
    setError("");
    try {
      await register(form);
      navigate("/citizen");
    } catch (err) {
      setErrors(fieldErrors(err));
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="container section auth-wrap single">
      <div className="card auth-card">
        <h1>Citizen registration</h1>
        <Alert>{error}</Alert>
        <form onSubmit={submit} className="form">
          <label>Full name<input value={form.name} onChange={set("name")} required />{errors.name && <span className="field-error">{errors.name}</span>}</label>
          <label>Email<input type="email" value={form.email} onChange={set("email")} required />{errors.email && <span className="field-error">{errors.email}</span>}</label>
          <label>Mobile number<input value={form.mobile} onChange={set("mobile")} placeholder="10-digit mobile" required />{errors.mobile && <span className="field-error">{errors.mobile}</span>}</label>
          <label>Password<input type="password" value={form.password} onChange={set("password")} required autoComplete="new-password" />
            <small className="muted">At least 8 characters with letters and numbers.</small>
            {errors.password && <span className="field-error">{errors.password}</span>}</label>
          <button className="btn btn-primary btn-block" disabled={busy}>{busy ? "Creating account..." : "Register"}</button>
        </form>
        <p className="muted center">Already registered? <Link to="/login">Login</Link></p>
      </div>
    </div>
  );
}
