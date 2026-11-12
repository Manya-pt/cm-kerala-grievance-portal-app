import { useEffect, useState } from "react";
import api, { errorMessage } from "../../api";
import { Alert, Loader } from "../../components/UI";

export default function Departments() {
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/departments").then((r) => setItems(r.data)).catch((e) => setError(errorMessage(e)));
  }, []);

  return (
    <div className="container section">
      <h1>Departments</h1>
      <p className="lead">Sample government departments that receive grievances forwarded by the CMO.</p>
      <Alert>{error}</Alert>
      {!items && !error ? <Loader /> : (
        <div className="card-grid">
          {items?.map((d) => (
            <div className="card" key={d.id}>
              <span className="dept-code">{d.code}</span>
              <h3>{d.name}</h3>
              <p className="muted">{d.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
