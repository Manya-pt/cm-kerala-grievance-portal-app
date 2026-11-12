import { useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { dashboardPath, useAuth } from "../AuthContext";

const links = [
  ["/", "Home"],
  ["/about", "About Us"],
  ["/how-it-works", "How It Works"],
  ["/departments", "Departments"],
  ["/track", "Track"],
  ["/faq", "FAQ"],
  ["/contact", "Contact"],
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  return (
    <>
      <div className="disclaimer">
        Recruitment prototype for a WhiteMatrix machine test. Not affiliated with or endorsed by the
        Government of Kerala or the Chief Minister's Office. All data is fictional.
      </div>
      <header className="header">
        <div className="container header-inner">
          <Link to="/" className="brand" onClick={() => setOpen(false)}>
            <span className="brand-mark">✓</span>
            <span>
              <strong>CM Kerala</strong>
              <small>Public Grievance Redressal Portal</small>
            </span>
          </Link>
          <button className="menu-btn" onClick={() => setOpen(!open)} aria-label="Menu">☰</button>
          <nav className={open ? "nav open" : "nav"} onClick={() => setOpen(false)}>
            {links.map(([to, label]) => (
              <NavLink key={to} to={to} end={to === "/"}>{label}</NavLink>
            ))}
            {user ? (
              <>
                <NavLink to={dashboardPath(user.role)} className="nav-cta">Dashboard</NavLink>
                <button className="link-btn" onClick={() => { logout(); navigate("/"); }}>Logout</button>
              </>
            ) : (
              <NavLink to="/login" className="nav-cta">Login</NavLink>
            )}
          </nav>
        </div>
      </header>
      <main>
        <Outlet />
      </main>
      <footer className="footer">
        <div className="container footer-grid">
          <div>
            <strong>CM Kerala Grievance Portal</strong>
            <p>A prototype showing how citizens, the CMO and departments can work together to resolve public grievances transparently.</p>
          </div>
          <div>
            <strong>Quick links</strong>
            <p><Link to="/citizen/submit">Submit grievance</Link><br /><Link to="/track">Track grievance</Link><br /><Link to="/faq">FAQ</Link></p>
          </div>
          <div>
            <strong>Prototype notice</strong>
            <p>Built for a recruitment assessment. Fictional sample data only. Do not submit real personal grievances.</p>
          </div>
        </div>
        <div className="container footer-bottom">© 2026 Recruitment prototype · Not an official government website</div>
      </footer>
    </>
  );
}
