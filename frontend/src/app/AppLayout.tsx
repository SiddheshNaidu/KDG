import { useRef } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { LogoMark } from "../landing-v2/art";
import { useAuth } from "./auth";
import "./app.css";

export default function AppLayout() {
  const { session, signOut } = useAuth();
  const mail = session?.user.email ?? "";
  const bar = useRef<HTMLElement>(null);

  return (
    <div className="kd">
      <div className="kd-bg" aria-hidden="true"><i /><i /><i /></div>
      <header className="kd-bar" ref={bar}>
        <div className="kd-bar__in">
          <Link to="/app" className="kd-brand">
            <LogoMark className="kd-brand__mark" />
            <span>KDG</span>
          </Link>
          <nav className="kd-nav" aria-label="App">
            <NavLink to="/app" end>Library</NavLink>
            <NavLink to="/app/new">Map a syllabus</NavLink>
          </nav>
          <div className="kd-user">
            <span className="kd-avatar" title={mail}>{(mail[0] ?? "?").toUpperCase()}</span>
            <span className="kd-user__mail">{mail}</span>
            <button className="kd-btn kd-btn--ghost kd-btn--sm" onClick={signOut}>Sign out</button>
          </div>
        </div>
      </header>
      <main className="kd-main">
        <Outlet />
      </main>
    </div>
  );
}
