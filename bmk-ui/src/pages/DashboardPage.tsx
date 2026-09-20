import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchDashboard } from "../api/auth";
import { useAuth } from "../auth/AuthContext";
import SiteHeader from "../components/SiteHeader";
import SikshavahiniButton from "../components/SikshavahiniButton";
import { useSchoolContent } from "../content/SchoolContentContext";
import type { DashboardPayload } from "../types/auth";
import {
  adminClassesPath,
  adminCommunicationPath,
  adminRequestsPath,
  adminUsersPath,
  myClassesPath,
  teacherCommunicationPath,
  teacherRequestsPath,
} from "../utils/routes";

const ROLE_LABELS = {
  ADMIN: "Administrator",
  TEACHER: "Teacher",
  STUDENT: "Student",
} as const;

export default function DashboardPage() {
  const { school, schoolSlug } = useSchoolContent();
  const { user } = useAuth();
  const [payload, setPayload] = useState<DashboardPayload | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) return;
    fetchDashboard(user.role)
      .then(setPayload)
      .catch(() => setError("Could not load role dashboard from the API."));
  }, [user]);

  if (!user) return null;

  return (
    <div className="page-shell">
      <SiteHeader />

      <div className="dash-shell">
        <header className="dash-header compact">
          <div>
            <p className="brand light">{school.school_name || schoolSlug}</p>
            <h1>{ROLE_LABELS[user.role]} Dashboard</h1>
          </div>
        </header>

        <section className="dash-panel">
          <p className="welcome">
            Signed in as <strong>({user.email || "no email"})</strong>
          </p>
          <p className="role-badge">{user.role}</p>

          {error && <p className="error">{error}</p>}

          {payload && (
            <>
              <p>{payload.message}</p>
              <h2>Capabilities</h2>
              <ul>
                {payload.capabilities.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </>
          )}

          {user.role === "ADMIN" && (
            <section className="admin-cta">
              {typeof payload?.pending_activations === "number" &&
                payload.pending_activations > 0 && (
                  <p>
                    {payload.pending_activations} user
                    {payload.pending_activations === 1 ? "" : "s"} waiting for
                    activation.
                  </p>
                )}
              <div className="home-actions">
                <Link to={adminUsersPath()} className="home-btn">
                  Manage Users
                </Link>
                <Link to={adminClassesPath()} className="home-btn secondary">
                  Manage Classes
                </Link>
                <Link to={adminRequestsPath()} className="home-btn secondary">
                  User Requests
                </Link>
              </div>
            </section>
          )}

          {(user.role === "TEACHER" || user.role === "STUDENT") && (
            <div className="home-actions">
              <Link to={myClassesPath(user.role)} className="home-btn">
                My Classes
              </Link>
              <Link to={adminCommunicationPath()} className="home-btn">
                Communicate with the admin team
              </Link>
              {user.role === "STUDENT" && (
                <Link
                  to={teacherCommunicationPath()}
                  className="home-btn secondary"
                >
                  Communicate with your teacher
                </Link>
              )}
              {user.role === "TEACHER" && (
                <Link to={teacherRequestsPath()} className="home-btn secondary">
                  Student Requests
                </Link>
              )}
            </div>
          )}

          <p className="admin-cta siksha-cta">
            <SikshavahiniButton className="home-btn" />
          </p>
        </section>
      </div>
    </div>
  );
}
