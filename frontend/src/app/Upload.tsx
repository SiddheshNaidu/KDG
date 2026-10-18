import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { analyze, type Subject } from "./api";
import { useAuth } from "./auth";
import { saveSyllabus } from "./store";
import { MapArt } from "./ui";
import { useReveal } from "./motion";

const STEPS = [
  ["Drop your PDF", "A Mumbai University syllabus."],
  ["Pick a subject", "If the PDF holds several."],
  ["Get your map", "Order, key topics and gaps."],
];

export default function Upload() {
  const { session } = useAuth();
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [phase, setPhase] = useState<"idle" | "loading" | "pick">("idle");
  const [error, setError] = useState("");
  const [dragging, setDragging] = useState(false);
  const root = useRef<HTMLDivElement>(null);
  useReveal(root, "[data-in]", [phase], { stagger: 0.07 });

  const run = async (pdf: File, subject?: string) => {
    setPhase("loading");
    setError("");
    try {
      const data = await analyze(pdf, subject);
      if (data.needs_subject) {
        setSubjects(data.subjects);
        setPhase("pick");
        return;
      }
      saveSyllabus(session!.user.id, {
        analysis_id: data.analysis_id,
        course_code: data.course_code,
        course_title: data.course_title,
      });
      navigate(`/app/s/${data.analysis_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setPhase(subject ? "pick" : "idle");
    }
  };

  const pickFile = (pdf?: File | null) => {
    if (!pdf) return;
    if (!pdf.name.toLowerCase().endsWith(".pdf")) {
      setError("Please choose a PDF file.");
      return;
    }
    setFile(pdf);
    run(pdf);
  };

  return (
    <div className="kd-page kd-upload" ref={root}>
      <div className="kd-upload__copy">
        <span className="kd-eyebrow" data-in>Map a syllabus</span>
        <h1 className="kd-h1" data-in>{phase === "pick" ? "Which subject?" : "Upload your syllabus"}</h1>
        <p className="kd-lead" data-in>
          {phase === "pick"
            ? "This PDF holds several subjects. Pick the one you want to map."
            : "We read the topics, work out which ones lead to which, and give you a study order. Your PDF is not saved."}
        </p>
        {phase !== "pick" && (
          <ol className="kd-steps">
            {STEPS.map(([t, d], i) => (
              <li key={t} data-in>
                <span>{i + 1}</span>
                <div><b>{t}</b><small>{d}</small></div>
              </li>
            ))}
          </ol>
        )}
      </div>

      <div className="kd-upload__panel" data-in>
        {phase === "idle" && (
          <label
            className={`kd-drop ${dragging ? "on" : ""}`}
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragging(false);
              pickFile(e.dataTransfer.files?.[0]);
            }}
          >
            <input type="file" accept=".pdf,application/pdf" hidden onChange={(e) => pickFile(e.target.files?.[0])} />
            <MapArt className="kd-drop__art" />
            <strong>Choose a PDF</strong>
            <span>or drag it here</span>
          </label>
        )}

        {phase === "loading" && (
          <div className="kd-loading">
            <div className="kd-orbit" aria-hidden="true"><i /><i /><i /></div>
            <strong>Reading {file?.name ?? "your syllabus"}</strong>
            <span>This can take up to a minute the first time.</span>
            <div className="kd-bar-load" aria-hidden="true"><i /></div>
          </div>
        )}

        {phase === "pick" && (
          <div className="kd-subjects">
            {subjects.map((s) => (
              <button
                key={`${s.course_code}-${s.course_title}`}
                className="kd-subject"
                onClick={() => file && run(file, `${s.course_code} ${s.course_title}`.trim())}
              >
                <b>{s.course_code}</b>
                <span>{s.course_title}</span>
              </button>
            ))}
            <button
              className="kd-link"
              onClick={() => {
                setPhase("idle");
                setFile(null);
                setError("");
              }}
            >
              Use a different PDF
            </button>
          </div>
        )}

        {error && <p className="kd-error" role="alert">{error}</p>}
      </div>
    </div>
  );
}
