// Static content pages: About Us, How It Works, FAQ.
import { useState } from "react";
import { Link } from "react-router-dom";

export function About() {
  return (
    <div className="container section narrow">
      <h1>About the initiative</h1>
      <p className="lead">
        The CM Kerala Public Grievance Redressal Portal gives every citizen a direct, transparent channel
        to the Chief Minister's Office (CMO) for problems with public services.
      </p>
      <div className="card-grid two">
        <div className="card">
          <h3>Purpose</h3>
          <p>Make sure no citizen complaint is lost. Each grievance is recorded, routed to the responsible department and tracked until it is resolved.</p>
        </div>
        <div className="card">
          <h3>Vision</h3>
          <p>A responsive government where citizens can see exactly who is handling their issue and what action has been taken.</p>
        </div>
        <div className="card">
          <h3>Mission</h3>
          <p>Use simple digital tools and responsible AI to cut delays, improve accountability and help officials focus on urgent cases first.</p>
        </div>
        <div className="card">
          <h3>Objectives</h3>
          <ul>
            <li>Single online window for grievances from all 14 districts</li>
            <li>Unique reference number and full status history</li>
            <li>Time-bound action with overdue tracking and escalation</li>
            <li>Data-driven monitoring of departments and districts</li>
            <li>Citizen feedback after every resolution</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

const STEPS = [
  ["Submit", "Register, describe your issue, choose your district and optionally attach a photo or document. The AI assistant suggests a category, department and priority, which you can accept or change."],
  ["Reference number", "You instantly receive a unique reference number (for example CMK-2026-000123) to track your grievance."],
  ["CMO review", "The Chief Minister's Office reviews the grievance, together with an AI-generated summary and possible duplicate warnings. A human always makes the decision."],
  ["Department assignment", "The CMO forwards the grievance to the relevant department and officer."],
  ["Action", "The officer investigates, posts progress updates and submits an action-taken report to the CMO."],
  ["Resolution", "The CMO reviews the report. If satisfied, the grievance is marked resolved; otherwise it is sent back. You are notified on your dashboard and can give feedback or reopen it."],
];

export function HowItWorks() {
  return (
    <div className="container section narrow">
      <h1>How it works</h1>
      <p className="lead">Every grievance follows the same transparent workflow.</p>
      <ol className="steps">
        {STEPS.map(([title, text], i) => (
          <li key={title}>
            <span className="step-num">{i + 1}</span>
            <div><h3>{title}</h3><p>{text}</p></div>
          </li>
        ))}
      </ol>
      <div className="card">
        <h3>Status meanings</h3>
        <ul>
          <li><b>Submitted</b>: received, waiting for CMO review</li>
          <li><b>Under Review</b>: being reviewed by the CMO or forwarded to a department</li>
          <li><b>In Progress</b>: the department is acting on it</li>
          <li><b>Resolved</b>: action completed and verified by the CMO</li>
          <li><b>Reopened</b>: the citizen reported the issue is not fixed</li>
        </ul>
      </div>
      <p><Link to="/citizen/submit" className="btn btn-primary">Submit a grievance</Link></p>
    </div>
  );
}

const FAQS = [
  ["Who can submit a grievance?", "Any citizen with a registered account. Registration needs your name, email, mobile number and a password."],
  ["What can I complain about?", "Issues involving public infrastructure, water, electricity, healthcare, education, revenue, police, welfare, sanitation, transport, agriculture and other public services."],
  ["How do I track my grievance?", "Use the Track page with your reference number. No login is needed. Logged-in citizens can also see all their grievances on the dashboard."],
  ["Can I attach documents?", "Yes. You can attach one image (JPG/PNG) or PDF up to 5 MB as supporting evidence."],
  ["What does the AI assistant do?", "It reads your description and suggests a category, department and priority, writes a short summary for officials and flags possible duplicate complaints. It only suggests. You and the CMO make every decision."],
  ["How long will it take?", "Target times are 3 days for High, 7 days for Medium and 14 days for Low priority. Delayed grievances are flagged as overdue and can be escalated by the CMO."],
  ["What if I'm not satisfied with the resolution?", "Open the grievance from your dashboard and click Reopen with a reason. It goes back to the CMO for review."],
  ["Is this an official government website?", "No. This is a recruitment prototype using fictional data. Do not submit real grievances."],
];

export function FAQ() {
  const [open, setOpen] = useState(0);
  return (
    <div className="container section narrow">
      <h1>Frequently asked questions</h1>
      <div className="faq">
        {FAQS.map(([q, a], i) => (
          <div key={q} className={open === i ? "faq-item open" : "faq-item"}>
            <button onClick={() => setOpen(open === i ? -1 : i)}>
              {q}<span>{open === i ? "−" : "+"}</span>
            </button>
            {open === i && <p>{a}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
