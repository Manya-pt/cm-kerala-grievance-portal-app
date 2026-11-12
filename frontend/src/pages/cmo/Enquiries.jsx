import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { errorMessage } from "../../api";
import { Alert, Loader, formatDate } from "../../components/UI";

export default function Enquiries() {
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/contact-enquiries").then((r) => setItems(r.data)).catch((e) => setError(errorMessage(e)));
  }, []);

  return (
    <div className="container section">
      <Link to="/cmo">← Back to dashboard</Link>
      <h1>Contact enquiries</h1>
      <Alert>{error}</Alert>
      {!items ? <Loader /> : (
        <div className="card table-wrap">
          <table className="table">
            <thead><tr><th>Date</th><th>Name</th><th>Email</th><th>Subject</th><th>Message</th></tr></thead>
            <tbody>
              {items.map((e) => (
                <tr key={e.id}>
                  <td className="nowrap">{formatDate(e.created_at)}</td><td>{e.name}</td><td>{e.email}</td>
                  <td>{e.subject}</td><td>{e.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
