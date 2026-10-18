import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import StudyMap, { type MapMode } from "./StudyMap";
import {
  BlockedError,
  getAnalysis,
  getMissing,
  getStatus,
  loadProgress,
  setMastery,
  type Analysis,
  type Node,
  type Status,
} from "./api";
import { useAuth } from "./auth";
import { useReveal } from "./motion";
import { saveSyllabus } from "./store";
import { Arrow, Check, Ring, Star, Tabs, unitColor } from "./ui";

type Tab = "map" | "plan" | "order" | "revise";

const TABS: { id: Tab; label: string }[] = [
  { id: "map", label: "Concept map" },
  { id: "plan", label: "Plan a topic" },
  { id: "order", label: "Study order" },
  { id: "revise", label: "Revise first" },
];

/** Every topic that must be learned before `targetId` (walks accepted arrows backwards). */
function prerequisitesOf(targetId: string, edges: Analysis["edges"]): Set<string> {
  const parents: Record<string, string[]> = {};
  edges.filter((e) => e.band === "accepted").forEach((e) => (parents[e.target] ??= []).push(e.source));
  const found = new Set<string>();
  const stack = [targetId];
  while (stack.length) {
    for (const p of parents[stack.pop()!] ?? []) {
      if (!found.has(p)) {
        found.add(p);
        stack.push(p);
      }
    }
  }
  return found;
}

const stateText = { mastered: "Learned", ready: "Ready to learn", blocked: "Needs earlier topics first" } as const;

export default function Workspace() {
  const { id = "" } = useParams();
  const { session } = useAuth();
  const uid = session!.user.id;

  const [result, setResult] = useState<Analysis | null>(null);
  const [status, setStatus] = useState<Status | null>(null);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<Tab>("map");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [mode, setMode] = useState<MapMode>("all");
  const [showUnsure, setShowUnsure] = useState(false);
  const [missing, setMissing] = useState<{ id: string; name: string }[] | null>(null);
  const [blocked, setBlocked] = useState<{ topicId: string; missing: { id: string; name: string }[] } | null>(null);
  const [query, setQuery] = useState("");

  const headRef = useRef<HTMLDivElement>(null);
  const bodyRef = useRef<HTMLDivElement>(null);
  useReveal(headRef, "[data-in]", [Boolean(result)], { stagger: 0.07 });
  useReveal(bodyRef, "[data-in]", [tab, Boolean(result)], { stagger: 0.045, y: 14 });

  // load the saved analysis and this user's progress
  useEffect(() => {
    let live = true;
    setResult(null);
    setError("");
    (async () => {
      try {
        const data = await getAnalysis(id);
        if (!live) return;
        setResult(data);
        saveSyllabus(uid, { analysis_id: data.analysis_id, course_code: data.course_code, course_title: data.course_title });
        try {
          setStatus(await loadProgress(uid, data.analysis_id));
        } catch {
          setStatus(await getStatus(data.analysis_id, []));
        }
      } catch (err) {
        if (live) setError(err instanceof Error ? err.message : "Could not open this syllabus.");
      }
    })();
    return () => {
      live = false;
    };
  }, [id, uid]);

  const mastered = useMemo(
    () => Object.entries(status?.nodes ?? {}).filter(([, s]) => s.state === "mastered").map(([k]) => k),
    [status],
  );
  const masteredKey = mastered.join("|");
  const keyIds = useMemo(() => new Set((result?.bottlenecks ?? []).map((b) => b.id)), [result]);
  const prereqIds = useMemo(
    () => (result && selectedId ? prerequisitesOf(selectedId, result.edges) : new Set<string>()),
    [result, selectedId],
  );
  const selected = result?.nodes.find((n) => n.id === selectedId) ?? null;
  const stateOf = (nodeId: string) => status?.nodes[nodeId]?.state;

  // what is still missing before the chosen topic, given what is already learned
  useEffect(() => {
    if (!result || !selectedId) {
      setMissing(null);
      return;
    }
    let live = true;
    getMissing(result.analysis_id, selectedId, mastered)
      .then((r) => live && setMissing(r.missing))
      .catch(() => live && setMissing(null));
    return () => {
      live = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [result, selectedId, masteredKey]);

  const select = (nodeId: string | null) => {
    setSelectedId(nodeId);
    setBlocked(null);
    if (!nodeId) setMode("all");
  };

  const toggle = async (topicId: string, force = false) => {
    if (!result) return;
    const isDone = stateOf(topicId) === "mastered";
    try {
      setStatus(await setMastery(uid, result.analysis_id, topicId, !isDone, force));
      setBlocked(null);
    } catch (err) {
      if (err instanceof BlockedError) {
        setSelectedId(topicId);
        setBlocked({ topicId, missing: err.missing });
      } else setError(err instanceof Error ? err.message : "Could not save.");
    }
  };

  if (error && !result) {
    return (
      <div className="kd-page kd-center">
        <h1 className="kd-h1">Could not open this syllabus</h1>
        <p className="kd-error" role="alert">{error}</p>
        <Link className="kd-btn" to="/app">Back to the library</Link>
      </div>
    );
  }
  if (!result) {
    return (
      <div className="kd-page">
        <div className="kd-skel kd-skel--head" />
        <div className="kd-skel kd-skel--map" />
      </div>
    );
  }

  const topicCount = result.nodes.length;
  const learned = mastered.length;
  const matches = query.trim().length > 1
    ? result.nodes.filter((n) => n.name.toLowerCase().includes(query.trim().toLowerCase())).slice(0, 7)
    : [];

  const backgroundFor = selected
    ? result.missing_prerequisites.filter((m) => m.needed_for.some((t) => t.id === selected.id || prereqIds.has(t.id)))
    : [];

  const panel = selected && (
    <aside className="kd-panel" aria-label="Topic details">
      <button className="kd-panel__x" onClick={() => select(null)} aria-label="Close">×</button>
      <div className="kd-panel__tags">
        <span className="kd-chip" style={{ background: unitColor(selected.unit) }}>Unit {selected.unit}</span>
        {keyIds.has(selected.id) && <span className="kd-chip kd-chip--key"><Star size={11} /> Key topic</span>}
        {selected.is_start && <span className="kd-chip kd-chip--start">Start here</span>}
      </div>
      <h3 className="kd-panel__title">{selected.name}</h3>
      {stateOf(selected.id) && <p className={`kd-state ${stateOf(selected.id)}`}>{stateText[stateOf(selected.id)!]}</p>}

      <h4 className="kd-h4">Study these first{missing ? ` (${missing.length})` : ""}</h4>
      {missing === null ? (
        <p className="kd-muted">Loading…</p>
      ) : missing.length === 0 ? (
        <p className="kd-muted">Nothing. You are ready for this topic.</p>
      ) : (
        <ol className="kd-path">
          {missing.map((m) => (
            <li key={m.id}>
              <button className="kd-link" onClick={() => select(m.id)}>{m.name}</button>
            </li>
          ))}
        </ol>
      )}

      <div className="kd-panel__actions">
        <button className="kd-btn kd-btn--block" onClick={() => toggle(selected.id)}>
          {stateOf(selected.id) === "mastered" ? "Mark as not learned" : "Mark as learned"}
        </button>
        {tab === "map" && (
          <button className="kd-btn kd-btn--ghost kd-btn--block" onClick={() => setMode(mode === "path" ? "all" : "path")}>
            {mode === "path" ? "Show the whole syllabus" : "Show only its path"}
          </button>
        )}
      </div>

      {blocked && blocked.topicId === selected.id && (
        <div className="kd-warn" role="alert">
          <p>Not yet. Learn these first:</p>
          <ul>{blocked.missing.map((m) => <li key={m.id}>{m.name}</li>)}</ul>
          <button className="kd-btn kd-btn--ghost kd-btn--sm" onClick={() => toggle(selected.id, true)}>I already know these</button>
        </div>
      )}
    </aside>
  );

  // study order grouped by unit
  const units = [...new Set(result.study_flow.map((s) => s.unit))].sort((a, b) => a - b);
  const unitTitle = (u: number): string | undefined => result.nodes.find((n: Node) => n.unit === u)?.unit_title;

  let content: ReactNode = null;
  if (tab === "map") {
    content = (
      <>
        <div className="kd-toolbar" data-in>
          <div className="kd-search">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="2" /><path d="M11 11l3.5 3.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
            <input placeholder="Find a topic…" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Find a topic" />
            {matches.length > 0 && (
              <ul className="kd-search__list">
                {matches.map((n) => (
                  <li key={n.id}>
                    <button onClick={() => { select(n.id); setQuery(""); }}>
                      <i style={{ background: unitColor(n.unit) }} />{n.name}<small>Unit {n.unit}</small>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div className="kd-seg" role="group" aria-label="Map view">
            <button className={mode === "all" ? "on" : ""} onClick={() => setMode("all")}>Whole syllabus</button>
            <button className={mode === "path" ? "on" : ""} disabled={!selectedId} onClick={() => setMode("path")} title={selectedId ? "" : "Pick a topic first"}>Path to topic</button>
          </div>
          <label className="kd-switch">
            <input type="checkbox" checked={showUnsure} onChange={(e) => setShowUnsure(e.target.checked)} />
            <span />Show unsure links
          </label>
        </div>

        <div className={`kd-mapcard ${selected ? "has-panel" : ""}`} data-in>
          <StudyMap
            nodes={result.nodes}
            edges={result.edges}
            keyIds={keyIds}
            states={status?.nodes ?? null}
            selectedId={selectedId}
            mode={mode}
            showUnsure={showUnsure}
            onSelect={select}
          />
          <div className="kd-legend" aria-hidden="true">
            <span><i className="lg lg--sel" />Your pick</span>
            <span><i className="lg lg--pre" />Learn first</span>
            <span><i className="lg lg--done" />Learned</span>
            <span><Star size={11} />Key topic</span>
          </div>
          {panel}
        </div>
        <p className="kd-hint" data-in>Tip: click a topic to light up what leads to it. Arrows go from a topic to the topics that build on it; thicker means more confident.</p>
      </>
    );
  } else if (tab === "plan") {
    content = (
      <div className="kd-plan">
        <div>
          <label className="kd-field" data-in>
            <span>Which topic do you want to learn?</span>
            <select value={selectedId ?? ""} onChange={(e) => select(e.target.value || null)}>
              <option value="">Choose a topic…</option>
              {result.nodes.map((n) => <option key={n.id} value={n.id}>Unit {n.unit}: {n.name}</option>)}
            </select>
          </label>

          {!selected ? (
            <div className="kd-empty" data-in><b>Pick a topic</b><span>You will see exactly what to study first, in order.</span></div>
          ) : (
            <div className="kd-timeline" data-in>
              <h4 className="kd-h4">Your path ({(missing?.length ?? 0) + 1} steps)</h4>
              {missing === null ? <p className="kd-muted">Loading…</p> : (
                <ol>
                  {missing.map((m, i) => (
                    <li key={m.id}><span className="kd-timeline__n">{i + 1}</span><button className="kd-link" onClick={() => select(m.id)}>{m.name}</button></li>
                  ))}
                  <li className="goal"><span className="kd-timeline__n">★</span><b>{selected.name}</b><small>your goal</small></li>
                </ol>
              )}
              <button className="kd-btn kd-btn--sm" onClick={() => toggle(selected.id)}>
                {stateOf(selected.id) === "mastered" ? "Mark as not learned" : "Mark goal as learned"}
              </button>
              {blocked && blocked.topicId === selected.id && (
                <div className="kd-warn" role="alert">
                  <p>Not yet. Learn the steps above first.</p>
                  <button className="kd-btn kd-btn--ghost kd-btn--sm" onClick={() => toggle(selected.id, true)}>I already know these</button>
                </div>
              )}
            </div>
          )}
        </div>

        <div>
          <h4 className="kd-h4" data-in>Background it assumes{selected ? ` (${backgroundFor.length})` : ""}</h4>
          {!selected ? <p className="kd-muted" data-in>Choose a topic to see the background knowledge it needs.</p>
            : backgroundFor.length === 0 ? <p className="kd-muted" data-in>None. Nothing outside the syllabus is needed.</p>
            : (
              <div className="kd-stack">
                {backgroundFor.map((m) => (
                  <div key={m.name} className="kd-note" data-in><b>{m.name}</b><p>{m.reason}</p></div>
                ))}
              </div>
            )}
        </div>
      </div>
    );
  } else if (tab === "order") {
    content = (
      <div className="kd-order">
        {units.map((u) => {
          const steps = result.study_flow.filter((s) => s.unit === u);
          const done = steps.filter((s) => stateOf(s.id) === "mastered").length;
          return (
            <section key={u} className="kd-unit" data-in style={{ ["--u" as string]: unitColor(u) }}>
              <header>
                <span className="kd-chip" style={{ background: unitColor(u) }}>Unit {u}</span>
                <h3>{unitTitle(u) ?? ""}</h3>
                <small>{done}/{steps.length} learned</small>
              </header>
              <ol>
                {steps.map((s) => (
                  <li key={s.id} className={stateOf(s.id) ?? ""}>
                    <span className="kd-order__n">{s.step}</span>
                    <div className="kd-order__t">
                      <button className="kd-link" onClick={() => { select(s.id); setTab("map"); }}>{s.name}</button>
                      <small>{s.prerequisites.length ? `After: ${s.prerequisites.slice(0, 3).join(", ")}${s.prerequisites.length > 3 ? ` +${s.prerequisites.length - 3}` : ""}` : "You can start here"}</small>
                    </div>
                    <button className={`kd-tick ${stateOf(s.id) === "mastered" ? "on" : ""}`} onClick={() => toggle(s.id)} aria-label={stateOf(s.id) === "mastered" ? "Mark as not learned" : "Mark as learned"}>
                      <Check size={15} />
                    </button>
                  </li>
                ))}
              </ol>
            </section>
          );
        })}
      </div>
    );
  } else {
    content = (
      <>
        <p className="kd-lead kd-lead--sm" data-in>Background this syllabus assumes you already know but never teaches. Brush up on these first.</p>
        {result.missing_prerequisites.length === 0 ? (
          <div className="kd-empty" data-in><b>Nothing to revise</b><span>No missing background was found for this syllabus.</span></div>
        ) : (
          <div className="kd-grid kd-grid--notes">
            {result.missing_prerequisites.map((m, i) => (
              <article key={m.name} className="kd-note kd-note--big" data-in style={{ ["--u" as string]: unitColor(i + 1) }}>
                <span className="kd-note__dot" />
                <b>{m.name}</b>
                <p>{m.reason}</p>
                {m.needed_for.length > 0 && (
                  <div className="kd-tags">{m.needed_for.slice(0, 4).map((t) => <span key={t.id}>{t.name}</span>)}{m.needed_for.length > 4 && <span>+{m.needed_for.length - 4}</span>}</div>
                )}
              </article>
            ))}
          </div>
        )}
      </>
    );
  }

  return (
    <div className="kd-page kd-work">
      <div className="kd-work__head" ref={headRef}>
        <div className="kd-work__title">
          <Link className="kd-back" to="/app" data-in><Arrow size={14} />Library</Link>
          <span className="kd-eyebrow" data-in>{result.course_code}</span>
          <h1 className="kd-h1" data-in>{result.course_title}</h1>
          <div className="kd-stats" data-in>
            <span><b>{topicCount}</b> topics</span>
            <span><b>{result.bottlenecks.length}</b> key topics</span>
            <span><b>{result.start_nodes.length}</b> start here</span>
            <span><b>{learned}</b> learned</span>
          </div>
        </div>
        <div data-in><Ring value={status?.progress_percent ?? 0} /></div>
      </div>

      <Tabs items={TABS} value={tab} onChange={setTab} />

      <div className="kd-work__body" ref={bodyRef} key={tab}>{content}</div>
      {error && <p className="kd-error" role="alert">{error}</p>}
    </div>
  );
}
