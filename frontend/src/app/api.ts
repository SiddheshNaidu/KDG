// Calls to the KDG backend (FastAPI). Base URL can be overridden with VITE_API_URL.
const BASE = (import.meta.env.VITE_API_URL as string | undefined) || "http://127.0.0.1:8000/api/v1";

export type Node = { id: string; name: string; unit: number; unit_title?: string; depth: number; kahn_index: number; is_start: boolean };
export type Edge = { source: string; target: string; confidence: number; band: "accepted" | "uncertain"; redundant: boolean };
export type Step = { step: number; id: string; name: string; unit: number; level: number; prerequisites: string[]; prerequisite_ids: string[] };
export type Bottleneck = { id: string; name: string; unlocks: number; direct: number };
export type Background = { name: string; reason: string; needed_for: { id: string; name: string }[] };
export type Subject = { course_code: string; course_title: string };

export type Analysis = {
  analysis_id: string;
  course_code?: string;
  course_title?: string;
  nodes: Node[];
  edges: Edge[];
  kahn_order: string[];
  start_nodes: string[];
  study_flow: Step[];
  bottlenecks: Bottleneck[];
  missing_prerequisites: Background[];
};

export type NodeState = { state: "mastered" | "ready" | "blocked"; is_start: boolean; waiting_on: string[] };
export type Status = {
  nodes: Record<string, NodeState>;
  start_nodes: string[];
  ready: string[];
  next_up: string[];
  progress_percent: number;
};

export class BlockedError extends Error {
  missing: { id: string; name: string }[];
  constructor(missing: { id: string; name: string }[]) {
    super("blocked");
    this.missing = missing;
  }
}

function message(data: unknown, fallback: string): string {
  const d = (data as { detail?: unknown } | null)?.detail;
  if (typeof d === "string") return d;
  const reason = (d as { error?: string } | undefined)?.error;
  if (reason === "not_a_syllabus") return "This file does not look like a syllabus. Try another PDF.";
  if (reason === "low_confidence") return "We could not read the topics in this PDF reliably. Try another PDF.";
  if (reason === "subject_not_found") return "That subject was not found in the PDF.";
  return fallback;
}

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, init);
  } catch {
    throw new Error("Could not reach the server. Make sure the backend is running on port 8000.");
  }
  const data = await res.json().catch(() => null);
  if (res.status === 409) {
    const d = (data as { detail?: { missing?: { id: string; name: string }[] } } | null)?.detail;
    throw new BlockedError(d?.missing ?? []);
  }
  if (!res.ok) throw new Error(message(data, "Something went wrong. Please try again."));
  return data as T;
}

const json = (body: unknown): RequestInit => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export type AnalyzeResult = ({ needs_subject: true; subjects: Subject[] } | ({ needs_subject?: false } & Analysis));

export function analyze(file: File, subject?: string): Promise<AnalyzeResult> {
  const form = new FormData();
  form.append("file", file);
  if (subject) form.append("subject", subject);
  return call<AnalyzeResult>("/analyze", { method: "POST", body: form });
}

export const getStatus = (analysisId: string, mastered: string[], targetId?: string | null) =>
  call<Status>("/progress/status", json({ analysis_id: analysisId, mastered, target_id: targetId ?? undefined }));

export const getMissing = (analysisId: string, targetId: string, known: string[]) =>
  call<{ missing: { id: string; name: string }[]; known_percent: number; total_prerequisites: number }>(
    "/analytics/missing-prerequisites",
    json({ analysis_id: analysisId, target_concept_id: targetId, known_concept_ids: known }),
  );

export const setMastery = (userId: string, analysisId: string, topicId: string, mastered: boolean, force = false) =>
  call<Status & { mastered?: string[] }>(
    "/progress/mastery",
    json({ user_id: userId, analysis_id: analysisId, topic_id: topicId, mastered, force }),
  );

export const loadProgress = (userId: string, analysisId: string) =>
  call<Status & { mastered?: string[] }>(`/progress/${userId}/${analysisId}`);

export const getAnalysis = (analysisId: string) => call<Analysis>(`/analysis/${analysisId}`);
