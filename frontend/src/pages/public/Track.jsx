import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import api, { errorMessage } from "../../api";
import { Alert, PriorityBadge, StatusBadge, Timeline, formatDate } from "../../components/UI";

export default function Track() {
  const [params, setParams] = useSearchParams();
  const [ref, setRef] = useState(params.get("ref") || "");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const lookup = async (value) => {
    if (!value.trim()) return;
    setBusy(true);
    setError("");
    setResult(null);
    try {
      setResult((await api.get(`/track/${encodeURIComponent(value.trim())}`)).data);
      setParams({ ref: value.trim().toUpperCase() });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    if (params.get("ref")) lookup(params.get("ref"));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="container section narrow">
      <h1>Track your grievance</h1>
      <p className="lead">Enter the reference number you received after submitting (for example CMK-2026-000001).</p>
      <form className="search-bar" onSubmit={(e) => { e.preventDefault(); lookup(ref); }}>
        <input value={ref} onChange={(e) => setRef(e.target.value)} placeholder="CMK-2026-000001" aria-label="Reference number" />
        <button className="btn btn-primary" disabled={busy}>{busy ? "Searching..." : "Track"}</button>
      </form>
      <Alert>{error}</Alert>
      {result && (
        <div className="card">
          <div className="detail-head">
            <div>
              <span className="ref">{result.ref_id}</span>
              <h2>{result.subject}</h2>
              <p className="muted">{result.district} · {result.category} · Submitted {formatDate(result.created_at)}</p>
            </div>
            <div className="badges"><StatusBadge status={result.status} /><PriorityBadge priority={result.priority} /></div>
          </div>
          <p><b>Assigned department:</b> {result.department}</p>
          <h3>Status history</h3>
          <Timeline history={result.history} />
        </div>
      )}
    </div>
  );
}
