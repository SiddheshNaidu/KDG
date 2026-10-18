import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { loadProgress } from "./api";
import { useAuth } from "./auth";
import { listSyllabuses, removeSyllabus } from "./store";
import { Arrow, unitColor } from "./ui";
import { useReveal } from "./motion";

type Info = { percent: number; topics: number } | null;

export default function Syllabuses() {
  const { session } = useAuth();
  const uid = session!.user.id;
  const [items, setItems] = useState(() => listSyllabuses(uid));
  const [info, setInfo] = useState<Record<string, Info>>({});
  const root = useRef<HTMLDivElement>(null);
  useReveal(root, "[data-in]", [items.length], { stagger: 0.07 });

  // progress and topic count for each card
  useEffect(() => {
    let live = true;
    items.forEach((s) =>
      loadProgress(uid, s.analysis_id)
        .then((p) => live && setInfo((m) => ({ ...m, [s.analysis_id]: { percent: p.progress_percent, topics: Object.keys(p.nodes).length } })))
        .catch(() => live && setInfo((m) => ({ ...m, [s.analysis_id]: null }))),
    );
    return () => {
      live = false;
    };
  }, [items, uid]);

  return (
    <div className="kd-page" ref={root}>
      <header className="kd-pagehead">
        <div>
          <span className="kd-eyebrow" data-in>Your library</span>
          <h1 className="kd-h1" data-in>Study maps</h1>
        </div>
        <Link className="kd-btn" to="/app/new" data-in>Map a syllabus <Arrow /></Link>
      </header>

      <div className="kd-grid">
        <Link to="/app/new" className="kd-card kd-card--new" data-in>
          <span className="kd-plus">+</span>
          <strong>Map a new syllabus</strong>
          <small>Upload a PDF and get a study order.</small>
        </Link>

        {items.map((s, i) => {
          const d = info[s.analysis_id];
          return (
            <article key={s.analysis_id} className="kd-card" data-in style={{ ["--u" as string]: unitColor(i + 1) }}>
              <div className="kd-card__band" />
              <span className="kd-chip">{s.course_code ?? "Syllabus"}</span>
              <h3>{s.course_title ?? "Untitled syllabus"}</h3>
              <div className="kd-meter" aria-label="Progress"><i style={{ width: `${d?.percent ?? 0}%` }} /></div>
              <div className="kd-card__meta">
                <span>{d === undefined ? "…" : d === null ? "Not available" : `${d.topics} topics · ${Math.round(d.percent)}% learned`}</span>
                <small>{new Date(s.created).toLocaleDateString()}</small>
              </div>
              <div className="kd-card__actions">
                <Link className="kd-btn kd-btn--sm" to={`/app/s/${s.analysis_id}`}>Open <Arrow size={14} /></Link>
                <button
                  className="kd-btn kd-btn--ghost kd-btn--sm"
                  onClick={() => {
                    removeSyllabus(uid, s.analysis_id);
                    setItems(listSyllabuses(uid));
                  }}
                >
                  Remove
                </button>
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
}
