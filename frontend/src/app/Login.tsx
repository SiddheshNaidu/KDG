import { useRef, useState, type FormEvent } from "react";
import { Link, Navigate, useSearchParams } from "react-router-dom";
import { supabase, configured } from "./supabase";
import { useAuth } from "./auth";
import { MapArt } from "./ui";
import { useReveal } from "./motion";
import { LogoMark } from "../landing-v2/art";
import "./app.css";

export default function Login() {
  const { session, loading } = useAuth();
  const [params] = useSearchParams();
  const raw = params.get("next") ?? "/app/new";
  const next = raw.startsWith("/app") ? raw : "/app/new";

  const [mode, setMode] = useState<"in" | "up">("in");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const root = useRef<HTMLDivElement>(null);
  useReveal(root, "[data-in]", [], { y: 22, stagger: 0.07 });

  if (!loading && session) return <Navigate to={next} replace />;

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    setInfo("");
    try {
      if (mode === "in") {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
      } else {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: { emailRedirectTo: `${location.origin}${next}` },
        });
        if (error) throw error;
        if (!data.session) setInfo("Check your email and click the link to confirm your account, then sign in.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setBusy(false);
    }
  };

  const google = async () => {
    setError("");
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: `${location.origin}${next}` },
    });
    if (error) setError(error.message);
  };

  return (
    <div className="kd kd-auth" ref={root}>
      <aside className="kd-auth__art">
        <Link to="/" className="kd-brand kd-brand--light">
          <LogoMark className="kd-brand__mark" />
          <span>KDG</span>
        </Link>
        <div className="kd-auth__copy">
          <h2 data-in>Study in the<br />right order.</h2>
          <p data-in>Upload a syllabus. See which topics lead to which, what to learn first, and what you are missing.</p>
        </div>
        <MapArt className="kd-auth__map" />
      </aside>

      <section className="kd-auth__form">
        <div className="kd-auth__card">
          <h1 data-in>{mode === "in" ? "Welcome back" : "Create your account"}</h1>
          <p className="kd-muted" data-in>{mode === "in" ? "Sign in to upload a syllabus and keep your progress." : "It takes a minute. Then upload your first syllabus."}</p>

          {!configured && <p className="kd-error" role="alert">Sign-in is not set up yet. Add the Supabase keys to frontend/.env.local.</p>}

          <button type="button" className="kd-btn kd-btn--ghost kd-btn--block" onClick={google} disabled={!configured} data-in>
            <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
              <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.6l6.7-6.7C35.6 2.4 30.2 0 24 0 14.6 0 6.5 5.4 2.6 13.2l7.8 6.1C12.3 13.6 17.7 9.5 24 9.5z" />
              <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.7c-.6 3-2.3 5.5-4.8 7.2l7.5 5.8c4.4-4.1 7.1-10.1 7.1-17.5z" />
              <path fill="#FBBC05" d="M10.4 28.7A14.5 14.5 0 0 1 9.5 24c0-1.6.3-3.2.9-4.7l-7.8-6.1A24 24 0 0 0 0 24c0 3.9.9 7.5 2.6 10.8l7.8-6.1z" />
              <path fill="#34A853" d="M24 48c6.2 0 11.5-2 15.3-5.6l-7.5-5.8c-2 1.4-4.7 2.3-7.8 2.3-6.3 0-11.7-4.1-13.6-9.8l-7.8 6.1C6.5 42.6 14.6 48 24 48z" />
            </svg>
            Continue with Google
          </button>

          <div className="kd-or" data-in><span>or use email</span></div>

          <form onSubmit={submit} className="kd-form">
            <label className="kd-field" data-in>
              <span>Email</span>
              <input type="email" required autoComplete="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} />
            </label>
            <label className="kd-field" data-in>
              <span>Password</span>
              <input
                type="password"
                required
                minLength={6}
                placeholder="At least 6 characters"
                autoComplete={mode === "in" ? "current-password" : "new-password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </label>
            <button className="kd-btn kd-btn--block" type="submit" disabled={busy || !configured} data-in>
              {busy ? "Please wait…" : mode === "in" ? "Sign in" : "Create account"}
            </button>
          </form>

          {error && <p className="kd-error" role="alert">{error}</p>}
          {info && <p className="kd-info" role="status">{info}</p>}

          <p className="kd-muted kd-swap" data-in>
            {mode === "in" ? "New here? " : "Already have an account? "}
            <button
              className="kd-link"
              type="button"
              onClick={() => {
                setMode(mode === "in" ? "up" : "in");
                setError("");
                setInfo("");
              }}
            >
              {mode === "in" ? "Create an account" : "Sign in"}
            </button>
          </p>
        </div>
      </section>
    </div>
  );
}
