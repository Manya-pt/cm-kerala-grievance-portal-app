import { useState } from "react";
import api, { errorMessage, fieldErrors } from "../../api";
import { Alert } from "../../components/UI";

const EMPTY = { name: "", email: "", subject: "", message: "" };

export default function Contact() {
  const [form, setForm] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const [status, setStatus] = useState({});
  const [busy, setBusy] = useState(false);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setErrors({});
    setStatus({});
    try {
      const r = await api.post("/contact", form);
      setStatus({ ok: r.data.message });
      setForm(EMPTY);
    } catch (err) {
      setErrors(fieldErrors(err));
      setStatus({ error: errorMessage(err) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="container section narrow">
      <h1>Contact us</h1>
      <p className="lead">For general questions about the portal. To report a problem, please <a href="/citizen/submit">submit a grievance</a>.</p>
      <div className="card">
        <Alert type="success">{status.ok}</Alert>
        <Alert>{status.error}</Alert>
        <form onSubmit={submit} className="form">
          <div className="form-row">
            <label>Name<input value={form.name} onChange={set("name")} required />{errors.name && <span className="field-error">{errors.name}</span>}</label>
            <label>Email<input type="email" value={form.email} onChange={set("email")} required />{errors.email && <span className="field-error">{errors.email}</span>}</label>
          </div>
          <label>Subject<input value={form.subject} onChange={set("subject")} required /></label>
          <label>Message<textarea rows={5} value={form.message} onChange={set("message")} required /></label>
          <button className="btn btn-primary" disabled={busy}>{busy ? "Sending..." : "Send message"}</button>
        </form>
      </div>
    </div>
  );
}
