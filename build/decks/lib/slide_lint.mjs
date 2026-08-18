// Language-tier lint for PROJECTED slide text.
//
// Three tiers (owner decision 2026-08-18):
//   1. Projected slides: student-facing only. Assume the teacher's chosen route.
//      No route menus, fallbacks, minute ranges, gradebook admin, teacher moves.
//   2. Student Guide (Canvas): student actions + support; platform-down route
//      only inside the expandable absence section.
//   3. Facilitator Guide + speaker notes: routes, fallbacks, pivots, timing.
//
// This module checks tier 1. Every daily builder and the weekly builder must
// run `lintSlideText` over the final inspect records and throw on failures.

export const BANNED_SLIDE_PATTERNS = [
  [/canvas or paper/i, "route menu on a projected slide"],
  [/\broutes?\b/i, "route language belongs in notes / facilitator guide"],
  [/fallback/i, "fallback language belongs in notes / facilitator guide"],
  [/\bminutes?\s+\d+\s*[–-]\s*\d+/i, "minute ranges belong in notes"],
  [/\bminors?\b|\bmajors?\b/i, "gradebook admin belongs in the facilitator guide"],
  [/\bmr\.?\s*lucero\b|\bmister\s+lucero\b/i, "wrong honorific"],
  [/classlink/i, "obsolete sign-in route"],
  [/\b(reopen|re-open|refresh)\b[^.]{0,60}\b(page|onenote|notebook)\b/i, "obsolete autosave test"],
  [/do not transfer|unsourced web search/i, "teacher policy language on a slide"],
  [/digital and physical routes/i, "route language on a slide"],
  [/\bpriority block\b/i, "teacher pacing label on a slide"],
  [/\bcheckpoint\b.*\bminute/i, "teacher timing language on a slide"],
];

/**
 * @param {Array<{kind:string, slide?:number, id?:string, text?:string}>} records
 *   Records from `presentation.inspect({ kind: "textbox,shape,table" })`.
 * @param {{ allow?: RegExp[] }} [options] Patterns that whitelist a matching text.
 * @returns {Array<{slide:number|undefined, id:string|undefined, reason:string, sample:string}>}
 */
export function lintSlideText(records, { allow = [] } = {}) {
  const failures = [];
  for (const record of records) {
    if (!["textbox", "shape", "table"].includes(record.kind)) continue;
    const text = String(record.text ?? "");
    if (!text.trim()) continue;
    if (allow.some((pattern) => pattern.test(text))) continue;
    for (const [pattern, reason] of BANNED_SLIDE_PATTERNS) {
      if (pattern.test(text)) {
        failures.push({ slide: record.slide, id: record.id, reason, sample: text.slice(0, 120) });
      }
    }
  }
  return failures;
}

/** Notes must carry the full teacher schema on every slide. */
export const REQUIRED_NOTES_LABELS = [
  "Time:",
  "Teacher move:",
  "Student action:",
  "Look-for:",
  "Pivot/trim:",
  "Recovery/access:",
  "[Sources]",
  "[/Sources]",
];

export function lintNotes(notesBySlide) {
  const failures = [];
  for (const [slide, notes] of notesBySlide) {
    const text = String(notes ?? "");
    const missing = REQUIRED_NOTES_LABELS.filter((label) => !text.includes(label));
    if (!text.trim() || missing.length) failures.push({ slide, missing });
    if (/\bmr\.?\s*lucero\b|\bmister\s+lucero\b/i.test(text)) failures.push({ slide, missing: ["honorific: Mr. Lucero"] });
  }
  return failures;
}

/** Records → Map(slide → concatenated notes text). */
export function notesMapFromRecords(records) {
  const map = new Map();
  for (const record of records) {
    if (record.kind !== "notes") continue;
    map.set(record.slide, `${map.get(record.slide) ?? ""}${record.text ?? ""}`);
  }
  return map;
}
