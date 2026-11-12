// All page routes. ProtectedRoute blocks pages a role should not see.
import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import Home from "./pages/public/Home";
import { About, FAQ, HowItWorks } from "./pages/public/InfoPages";
import Departments from "./pages/public/Departments";
import Contact from "./pages/public/Contact";
import Track from "./pages/public/Track";
import Login from "./pages/public/Login";
import Register from "./pages/public/Register";
import CitizenDashboard from "./pages/citizen/CitizenDashboard";
import SubmitGrievance from "./pages/citizen/SubmitGrievance";
import CmoDashboard from "./pages/cmo/CmoDashboard";
import Enquiries from "./pages/cmo/Enquiries";
import Officers from "./pages/cmo/Officers";
import OfficerDashboard from "./pages/officer/OfficerDashboard";
import GrievanceDetail from "./pages/GrievanceDetail";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/how-it-works" element={<HowItWorks />} />
        <Route path="/departments" element={<Departments />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/faq" element={<FAQ />} />
        <Route path="/track" element={<Track />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route element={<ProtectedRoute roles={["citizen"]} />}>
          <Route path="/citizen" element={<CitizenDashboard />} />
          <Route path="/citizen/submit" element={<SubmitGrievance />} />
        </Route>
        <Route element={<ProtectedRoute roles={["cmo"]} />}>
          <Route path="/cmo" element={<CmoDashboard />} />
          <Route path="/cmo/enquiries" element={<Enquiries />} />
          <Route path="/cmo/officers" element={<Officers />} />
        </Route>
        <Route element={<ProtectedRoute roles={["officer"]} />}>
          <Route path="/officer" element={<OfficerDashboard />} />
        </Route>
        <Route element={<ProtectedRoute roles={["citizen", "cmo", "officer"]} />}>
          <Route path="/grievances/:id" element={<GrievanceDetail />} />
        </Route>
        <Route path="*" element={<div className="container section"><h2>Page not found</h2></div>} />
      </Route>
    </Routes>
  );
}
