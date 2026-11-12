import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { errorMessage } from "../../api";
import { dashboardPath, useAuth } from "../../AuthContext";
import { Alert } from "../../components/UI";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const user = await login(email, password);
      const from = location.state?.from;
      navigate(from && from !== "/login" ? from : dashboardPath(user.role), { replace: true });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="container section auth-wrap single">
      <div className="card auth-card">
        <h1>Login</h1>
        <p className="muted">Citizens, CMO administrators and department officers log in here.</p>
        <Alert>{error}</Alert>
        <form onSubmit={submit} className="form">
          <label>Email<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="username" /></label>
          <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="current-password" /></label>
          <button className="btn btn-primary btn-block" disabled={busy}>{busy ? "Logging in..." : "Login"}</button>
        </form>
        <p className="muted center">New citizen? <Link to="/register">Create an account</Link></p>
      </div>
    </div>
  );
}
