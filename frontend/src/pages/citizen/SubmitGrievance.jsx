// Grievance form with the AI Grievance Assistant.
// The citizen clicks "Analyse with AI", reviews the suggestions and chooses whether to apply them.
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { errorMessage, fieldErrors } from "../../api";
import { Alert, PriorityBadge } from "../../components/UI";

export default function SubmitGrievance() {
  const navigate = useNavigate();
  const [meta, setMeta] = useState({ districts: [], categories: [] });
  const [form, setForm] = useState({ district: "", category: "", subject: "", description: "", priority: "" });
  const [file, setFile] = useState(null);
  const [ai, setAi] = useState(null);
  const [aiBusy, setAiBusy] = useState(false);
  const [aiError, setAiError] = useState("");
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.get("/meta").then((r) => setMeta(r.data)).catch(() => {});
  }, []);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const analyse = async () => {
    setAiBusy(true);
    setAiError("");
    try {
      const r = await api.post("/ai/analyze", {
        subject: form.subject, description: form.description, district: form.district,
      });
      setAi(r.data);
    } catch (err) {
      setAiError(errorMessage(err));
    } finally {
      setAiBusy(false);
    }
  };

  const applyAll = () => setForm({ ...form, category: ai.category, priority: ai.priority });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setErrors({});
    setError("");
    const data = new FormData();
    Object.entries(form).forEach(([k, v]) => v && data.append(k, v));
    if (file) data.append("attachment", file);
    try {
      const r = await api.post("/grievances", data);
      navigate("/citizen", { state: { newRef: r.data.ref_id } });
    } catch (err) {
      setErrors(fieldErrors(err));
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="container section">
      <h1>Submit a grievance</h1>
      <p className="muted">Fields marked * are required. Please use fictional details: this is a prototype.</p>
      <div className="submit-grid">
        <form className="card form" onSubmit={submit}>
          <Alert>{error}</Alert>
          <div className="form-row">
            <label>District *
              <select value={form.district} onChange={set("district")} required>
                <option value="">Select district</option>
                {meta.districts.map((d) => <option key={d}>{d}</option>)}
              </select>
              {errors.district && <span className="field-error">{errors.district}</span>}
            </label>
            <label>Category *
              <select value={form.category} onChange={set("category")} required>
                <option value="">Select category</option>
                {meta.categories.map((c) => <option key={c}>{c}</option>)}
              </select>
              {errors.category && <span className="field-error">{errors.category}</span>}
            </label>
          </div>
          <label>Subject *
            <input value={form.subject} onChange={set("subject")} maxLength={200} placeholder="Short title of the problem" required />
            {errors.subject && <span className="field-error">{errors.subject}</span>}
          </label>
          <label>Detailed description *
            <textarea rows={7} value={form.description} onChange={set("description")} placeholder="What is the problem, where exactly, since when, and how many people are affected?" required />
            {errors.description && <span className="field-error">{errors.description}</span>}
          </label>
          <label>Priority (optional)
            <select value={form.priority} onChange={set("priority")}>
              <option value="">Let the CMO decide (default Medium)</option>
              <option>Low</option><option>Medium</option><option>High</option>
            </select>
          </label>
          <label>Supporting image or document (optional)
            <input type="file" accept=".jpg,.jpeg,.png,.pdf" onChange={(e) => setFile(e.target.files[0] || null)} />
            <small className="muted">JPG, PNG or PDF, max 5 MB.</small>
            {errors.attachment && <span className="field-error">{errors.attachment}</span>}
          </label>
          <button className="btn btn-primary btn-lg" disabled={busy}>{busy ? "Submitting..." : "Submit grievance"}</button>
        </form>

        <aside className="card ai-panel">
          <h2>✨ AI Grievance Assistant</h2>
          <p className="muted">After writing the subject and description, let the AI suggest the right category, department and priority. You decide whether to use them.</p>
          <button type="button" className="btn btn-gold btn-block" onClick={analyse}
            disabled={aiBusy || (form.subject + form.description).length < 20}>
            {aiBusy ? "Analysing..." : "Analyse with AI"}
          </button>
          <Alert>{aiError}</Alert>
          {ai && (
            <div className="ai-result">
              <div className={ai.source === "fallback" ? "ai-source fallback" : "ai-source"}>
                {ai.source === "fallback" ? "⚠ Fallback (not AI)" : `Model: ${ai.source}`}
              </div>
              <dl>
                <dt>Suggested category</dt><dd>{ai.category}</dd>
                <dt>Suggested department</dt><dd>{ai.department || "—"}</dd>
                <dt>Suggested priority</dt><dd><PriorityBadge priority={ai.priority} /> <small className="muted">{ai.priority_reason}</small></dd>
                <dt>Summary for CMO</dt><dd>{ai.summary}</dd>
              </dl>
              {ai.duplicate_ref && (
                <Alert type="warning">
                  Possible duplicate of <b>{ai.duplicate_ref}</b>. {ai.duplicate_reason} You can still submit; the CMO will review it.
                </Alert>
              )}
              <button type="button" className="btn btn-outline btn-block" onClick={applyAll}>Apply category & priority</button>
              <p className="ai-notice">{ai.notice}</p>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
