// One grievance record. The same page shows different action panels for citizen, CMO and officer.
// The backend re-checks every permission, so hiding a button here is only for usability.
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api, { errorMessage, openAttachment } from "../api";
import { dashboardPath, useAuth } from "../AuthContext";
import { Alert, Loader, PriorityBadge, StatusBadge, Timeline, formatDate } from "../components/UI";

export default function GrievanceDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [g, setG] = useState(null);
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.get(`/grievances/${id}`).then((r) => setG(r.data)).catch((e) => setError(errorMessage(e)));
  }, [id]);

  // Runs an API action, refreshes the record and shows a message
  const act = async (fn, success) => {
    setBusy(true);
    setError("");
    setMsg("");
    try {
      const r = await fn();
      setG(r.data.grievance || r.data);
      setMsg(success);
      return true;
    } catch (err) {
      setError(errorMessage(err));
      return false;
    } finally {
      setBusy(false);
    }
  };

  if (!g) return <div className="container section">{error ? <Alert>{error}</Alert> : <Loader />}</div>;

  const pendingReport = g.reports.find((r) => r.review_status === "Pending");
  const supporting = g.attachments.filter((a) => a.kind === "supporting");

  return (
    <div className="container section wide">
      <Link to={dashboardPath(user.role)}>← Back to dashboard</Link>
      <div className="detail-head">
        <div>
          <span className="ref">{g.ref_id}</span>
          <h1>{g.subject}</h1>
          <p className="muted">
            {g.district} · {g.category} · Submitted {formatDate(g.created_at)}
            {g.citizen && user.role !== "citizen" && <> · by {g.citizen}</>}
          </p>
        </div>
        <div className="badges">
          <StatusBadge status={g.status} />
          <PriorityBadge priority={g.priority} />
          {g.overdue && <span className="tag tag-red">Overdue</span>}
          {g.escalated && <span className="tag tag-orange">Escalated</span>}
        </div>
      </div>
      <Alert type="success">{msg}</Alert>
      <Alert>{error}</Alert>

      <div className="detail-grid">
        <div>
          <div className="card">
            <h3>Complaint</h3>
            <p className="pre">{g.description}</p>
            <div className="meta-grid">
              <div><small>Department</small><b>{g.department || "Not yet assigned"}</b></div>
              <div><small>Officer</small><b>{g.officer || "—"}</b></div>
              <div><small>Target date</small><b>{formatDate(g.due_at, false)}</b></div>
              <div><small>Last updated</small><b>{formatDate(g.updated_at)}</b></div>
            </div>
            {g.citizen_contact && (
              <p className="muted">Citizen contact: {g.citizen_contact.email} · {g.citizen_contact.mobile}</p>
            )}
            <h4>Supporting attachments</h4>
            {supporting.length ? supporting.map((a) => (
              <button key={a.id} className="file-btn" onClick={() => openAttachment(a.id).catch(() => setError("Could not open file"))}>
                📎 {a.filename} <small>({Math.round(a.size / 1024)} KB)</small>
              </button>
            )) : <p className="muted">No attachments.</p>}
          </div>

          {user.role !== "citizen" && <AiPanel g={g} canRerun={user.role === "cmo"} busy={busy}
            onRerun={() => act(() => api.post(`/grievances/${g.id}/reanalyze`), "AI analysis refreshed.")} />}

          {g.reports.length > 0 && (
            <div className="card">
              <h3>Action-taken reports</h3>
              {g.reports.map((r) => (
                <div key={r.id} className="report">
                  <div className="report-head">
                    <b>{r.officer}</b><span className={`tag tag-${r.review_status === "Accepted" ? "green" : r.review_status === "Returned" ? "red" : "blue"}`}>{r.review_status}</span>
                    <small className="muted">{formatDate(r.created_at)}</small>
                  </div>
                  <p className="pre">{r.report}</p>
                  {r.files.map((f) => <button key={f.id} className="file-btn" onClick={() => openAttachment(f.id)}>📎 {f.filename}</button>)}
                  {r.cmo_remark && <p className="muted"><b>CMO remark:</b> {r.cmo_remark}</p>}
                </div>
              ))}
            </div>
          )}

          {g.feedback && (
            <div className="card">
              <h3>Citizen feedback</h3>
              <p className="stars">{"★".repeat(g.feedback.rating)}{"☆".repeat(5 - g.feedback.rating)}</p>
              <p>{g.feedback.comment}</p>
            </div>
          )}

          <div className="card">
            <h3>Status history & updates</h3>
            <Timeline history={g.history} />
          </div>
        </div>

        <aside>
          {user.role === "cmo" && <CmoActions g={g} act={act} busy={busy} pendingReport={pendingReport} />}
          {user.role === "officer" && <OfficerActions g={g} act={act} busy={busy} pendingReport={pendingReport} />}
          {user.role === "citizen" && <CitizenActions g={g} act={act} busy={busy} />}
        </aside>
      </div>
    </div>
  );
}

function AiPanel({ g, canRerun, onRerun, busy }) {
  const ai = g.ai;
  return (
    <div className="card ai-panel">
      <div className="section-head">
        <h3>✨ AI analysis <small className="muted">(suggestion only)</small></h3>
        {canRerun && <button className="btn btn-outline btn-sm" onClick={onRerun} disabled={busy}>Re-run AI</button>}
      </div>
      {ai.source && <div className={ai.source === "fallback" ? "ai-source fallback" : "ai-source"}>{ai.source === "fallback" ? "⚠ Fallback rules (not AI)" : `Source: ${ai.source}`}</div>}
      <p><b>Summary:</b> {ai.summary || "—"}</p>
      <div className="meta-grid">
        <div><small>Suggested department</small><b>{ai.department || "—"}</b></div>
        <div><small>Suggested category</small><b>{ai.category || "—"}</b></div>
        <div><small>Suggested priority</small><b>{ai.priority || "—"}</b></div>
      </div>
      {ai.duplicate_ref && <Alert type="warning">Possible duplicate of <Link to={`/track?ref=${ai.duplicate_ref}`}>{ai.duplicate_ref}</Link>. {ai.duplicate_reason} Human review needed.</Alert>}
    </div>
  );
}

// ---------------- CMO ----------------
function CmoActions({ g, act, busy, pendingReport }) {
  const [departments, setDepartments] = useState([]);
  const [officers, setOfficers] = useState([]);
  const [assign, setAssign] = useState({ department_id: "", officer_id: "", note: "" });
  const [remark, setRemark] = useState({ text: "", internal: true });
  const [review, setReview] = useState("");
  const [resolveNote, setResolveNote] = useState("");
  const [edit, setEdit] = useState({ priority: g.priority, category: g.category });
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    api.get("/departments").then((r) => {
      setDepartments(r.data);
      const suggested = r.data.find((d) => d.name === (g.department || g.ai.department));
      if (suggested) setAssign((a) => ({ ...a, department_id: String(suggested.id) }));
    });
    api.get("/meta").then((r) => setCategories(r.data.categories));
  }, [g.department, g.ai.department]);

  useEffect(() => {
    if (!assign.department_id) return setOfficers([]);
    api.get("/officers", { params: { department_id: assign.department_id } }).then((r) => {
      setOfficers(r.data);
      setAssign((a) => ({ ...a, officer_id: r.data[0] ? String(r.data[0].id) : "" }));
    });
  }, [assign.department_id]);

  const resolved = g.status === "Resolved";

  return (
    <>
      {["Submitted", "Reopened"].includes(g.status) && (
        <div className="card action-card">
          <h3>Review</h3>
          <button className="btn btn-primary btn-block" disabled={busy}
            onClick={() => act(() => api.patch(`/grievances/${g.id}/status`, { status: "Under Review", remark: "Grievance taken up for review." }), "Marked Under Review.")}>
            Mark as Under Review
          </button>
        </div>
      )}

      {pendingReport && (
        <div className="card action-card highlight">
          <h3>Review action-taken report</h3>
          <p className="pre small">{pendingReport.report}</p>
          <textarea rows={3} placeholder="Remark (required). Accepted remarks are visible to the citizen." value={review} onChange={(e) => setReview(e.target.value)} />
          <div className="btn-row">
            <button className="btn btn-success" disabled={busy || !review}
              onClick={async () => (await act(() => api.post(`/grievances/${g.id}/reports/${pendingReport.id}/review`, { decision: "accept", remark: review }), "Report accepted. Grievance resolved.")) && setReview("")}>Accept & resolve</button>
            <button className="btn btn-danger-outline" disabled={busy || !review}
              onClick={async () => (await act(() => api.post(`/grievances/${g.id}/reports/${pendingReport.id}/review`, { decision: "return", remark: review }), "Report returned to department.")) && setReview("")}>Return</button>
          </div>
        </div>
      )}

      {!resolved && (
        <div className="card action-card">
          <h3>{g.department ? "Re-assign department" : "Forward to department"}</h3>
          {g.ai.department && <p className="muted small">AI suggests: <b>{g.ai.department}</b></p>}
          <label>Department
            <select value={assign.department_id} onChange={(e) => setAssign({ ...assign, department_id: e.target.value })}>
              <option value="">Select department</option>
              {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </label>
          <label>Officer
            <select value={assign.officer_id} onChange={(e) => setAssign({ ...assign, officer_id: e.target.value })}>
              <option value="">Any officer in department</option>
              {officers.map((o) => <option key={o.id} value={o.id}>{o.name}</option>)}
            </select>
          </label>
          <textarea rows={2} placeholder="Instructions for the department (optional)" value={assign.note} onChange={(e) => setAssign({ ...assign, note: e.target.value })} />
          <button className="btn btn-primary btn-block" disabled={busy || !assign.department_id}
            onClick={() => act(() => api.post(`/grievances/${g.id}/assign`, assign), "Grievance forwarded.")}>Forward</button>
        </div>
      )}

      <div className="card action-card">
        <h3>Official priority & category</h3>
        <label>Priority
          <select value={edit.priority} onChange={(e) => setEdit({ ...edit, priority: e.target.value })}>
            <option>Low</option><option>Medium</option><option>High</option>
          </select>
        </label>
        <label>Category
          <select value={edit.category} onChange={(e) => setEdit({ ...edit, category: e.target.value })}>
            {categories.map((c) => <option key={c}>{c}</option>)}
          </select>
        </label>
        <div className="btn-row">
          {g.ai.priority && <button className="btn btn-outline btn-sm" onClick={() => setEdit({ priority: g.ai.priority, category: g.ai.category || edit.category })}>Use AI suggestion</button>}
          <button className="btn btn-primary btn-sm" disabled={busy}
            onClick={() => act(() => api.patch(`/grievances/${g.id}`, edit), "Details updated.")}>Save</button>
        </div>
      </div>

      <div className="card action-card">
        <h3>Add remark</h3>
        <textarea rows={3} value={remark.text} onChange={(e) => setRemark({ ...remark, text: e.target.value })} placeholder="Write a remark" />
        <label className="checkbox"><input type="checkbox" checked={remark.internal} onChange={(e) => setRemark({ ...remark, internal: e.target.checked })} /> Internal (hidden from citizen)</label>
        <button className="btn btn-outline btn-block" disabled={busy || !remark.text}
          onClick={async () => (await act(() => api.post(`/grievances/${g.id}/remarks`, { remark: remark.text, internal: remark.internal }), "Remark added.")) && setRemark({ text: "", internal: true })}>Add remark</button>
      </div>

      {!resolved && (
        <div className="card action-card">
          <h3>Escalate or close</h3>
          {!g.escalated && (
            <button className="btn btn-warning btn-block" disabled={busy}
              onClick={() => act(() => api.post(`/grievances/${g.id}/escalate`, { remark: "Escalated by CMO for urgent action due to delay." }), "Grievance escalated (priority set to High).")}>
              Escalate delayed grievance
            </button>
          )}
          <textarea rows={2} placeholder="Resolution remark (visible to citizen)" value={resolveNote} onChange={(e) => setResolveNote(e.target.value)} />
          <button className="btn btn-success btn-block" disabled={busy || !resolveNote}
            onClick={() => act(() => api.patch(`/grievances/${g.id}/status`, { status: "Resolved", remark: resolveNote }), "Marked resolved.")}>Mark resolved directly</button>
        </div>
      )}
    </>
  );
}

// ---------------- Officer ----------------
function OfficerActions({ g, act, busy, pendingReport }) {
  const [update, setUpdate] = useState("");
  const [report, setReport] = useState("");
  const [file, setFile] = useState(null);
  const [remark, setRemark] = useState("");

  const sendReport = async () => {
    const data = new FormData();
    data.append("report", report);
    if (file) data.append("attachment", file);
    if (await act(() => api.post(`/grievances/${g.id}/reports`, data), "Action-taken report submitted to CMO.")) {
      setReport("");
      setFile(null);
    }
  };

  if (g.status === "Resolved") return <div className="card action-card"><h3>Resolved</h3><p className="muted">This grievance has been closed by the CMO.</p></div>;
  if (g.status === "Reopened" || g.status === "Submitted") return <div className="card action-card"><h3>Waiting for CMO</h3><p className="muted">The CMO is reviewing this grievance again.</p></div>;

  return (
    <>
      <div className="card action-card">
        <h3>{g.status === "Under Review" ? "Start investigation" : "Progress update"}</h3>
        <textarea rows={3} value={update} onChange={(e) => setUpdate(e.target.value)} placeholder="Investigation remarks (visible to CMO and citizen)" />
        <button className="btn btn-primary btn-block" disabled={busy || !update}
          onClick={async () => (await act(() => api.patch(`/grievances/${g.id}/status`, { status: "In Progress", remark: update }), "Status updated.")) && setUpdate("")}>
          {g.status === "Under Review" ? "Start (set In Progress)" : "Post update"}
        </button>
      </div>

      <div className="card action-card highlight">
        <h3>Action-taken report</h3>
        {pendingReport ? <p className="muted">Your report is awaiting CMO review.</p> : (
          <>
            <textarea rows={5} value={report} onChange={(e) => setReport(e.target.value)} placeholder="Describe what was done to resolve the grievance" />
            <input type="file" accept=".jpg,.jpeg,.png,.pdf" onChange={(e) => setFile(e.target.files[0] || null)} />
            <button className="btn btn-success btn-block" disabled={busy || report.length < 10} onClick={sendReport}>Submit report to CMO</button>
          </>
        )}
      </div>

      <div className="card action-card">
        <h3>Internal note to CMO</h3>
        <textarea rows={2} value={remark} onChange={(e) => setRemark(e.target.value)} />
        <button className="btn btn-outline btn-block" disabled={busy || !remark}
          onClick={async () => (await act(() => api.post(`/grievances/${g.id}/remarks`, { remark, internal: true }), "Note added.")) && setRemark("")}>Add note</button>
      </div>
    </>
  );
}

// ---------------- Citizen ----------------
function CitizenActions({ g, act, busy }) {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [reason, setReason] = useState("");

  if (g.status !== "Resolved") {
    return (
      <div className="card action-card">
        <h3>What happens next?</h3>
        <p className="muted">
          {g.status === "Submitted" && "Your grievance is waiting for review by the Chief Minister's Office."}
          {g.status === "Under Review" && "The CMO is reviewing your grievance and has forwarded it, or will forward it, to the right department."}
          {g.status === "In Progress" && "The department is working on your grievance. Updates appear in the history below."}
          {g.status === "Reopened" && "You reopened this grievance. The CMO will review it again."}
        </p>
        <p className="muted small">Share your reference number <b>{g.ref_id}</b> to let others track it.</p>
      </div>
    );
  }
  return (
    <>
      {!g.feedback && (
        <div className="card action-card highlight">
          <h3>Rate the resolution</h3>
          <div className="star-input">
            {[1, 2, 3, 4, 5].map((n) => <button key={n} className={n <= rating ? "on" : ""} onClick={() => setRating(n)} aria-label={`${n} stars`}>★</button>)}
          </div>
          <textarea rows={3} placeholder="Comments (optional)" value={comment} onChange={(e) => setComment(e.target.value)} />
          <button className="btn btn-primary btn-block" disabled={busy}
            onClick={() => act(() => api.post(`/grievances/${g.id}/feedback`, { rating, comment }), "Thank you for your feedback.")}>Submit feedback</button>
        </div>
      )}
      <div className="card action-card">
        <h3>Not resolved?</h3>
        <textarea rows={3} placeholder="Explain why the issue is not resolved" value={reason} onChange={(e) => setReason(e.target.value)} />
        <button className="btn btn-danger-outline btn-block" disabled={busy || !reason}
          onClick={() => act(() => api.patch(`/grievances/${g.id}/status`, { status: "Reopened", remark: reason }), "Grievance reopened. The CMO will review it again.")}>Reopen grievance</button>
      </div>
    </>
  );
}
