// The list of syllabuses a signed-in user has analysed, kept in this browser per user id.
// (The results themselves come from the backend by analysis id; this list moves to the database later.)
export type SavedSyllabus = { analysis_id: string; course_code?: string; course_title?: string; created: string };

const key = (userId: string) => `kdg-syllabuses:${userId}`;

export function listSyllabuses(userId: string): SavedSyllabus[] {
  try {
    return JSON.parse(localStorage.getItem(key(userId)) ?? "[]");
  } catch {
    return [];
  }
}

export function saveSyllabus(userId: string, item: Omit<SavedSyllabus, "created">) {
  try {
    const rest = listSyllabuses(userId).filter((s) => s.analysis_id !== item.analysis_id);
    localStorage.setItem(key(userId), JSON.stringify([{ ...item, created: new Date().toISOString() }, ...rest]));
  } catch {
    /* storage blocked: the list just will not persist */
  }
}

export function removeSyllabus(userId: string, analysisId: string) {
  try {
    localStorage.setItem(key(userId), JSON.stringify(listSyllabuses(userId).filter((s) => s.analysis_id !== analysisId)));
  } catch {
    /* ignore */
  }
}
