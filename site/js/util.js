// Pure helpers: no DOM, no map, no shared state (so they can be tested with `node --test`).

export const REPO = "https://github.com/omidhey/world-history-map";
export const ISSUES = REPO + "/issues/new";

// Years are integers, negative = BCE, no year 0.
export function formatYear(year) {
  return year < 0 ? -year + " BCE" : year + " CE";
}

export function escapeHtml(text) {
  return String(text).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

// Stable colour per ruling power: the same SUBJECTO hashes to the same hue in every snapshot.
export function hashString(text) {
  let hash = 2166136261; // FNV-1a
  for (let i = 0; i < text.length; i++) {
    hash ^= text.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

export function colourFor(subjecto) {
  const hash = hashString(subjecto);
  const hue = hash % 360;
  const saturation = 45 + ((hash >>> 9) % 25); // 45–69 %
  const lightness = 55 + ((hash >>> 17) % 15); // 55–69 %
  return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

// "Suggest an edit" without a backend: a GitHub issue form pre-filled through URL parameters.
// Keys are the field ids in .github/ISSUE_TEMPLATE/<template>.
export function suggestEditUrl(template, title, fields) {
  const params = new URLSearchParams({ template, title, ...fields });
  return ISSUES + "?" + params.toString();
}

export function formatDates(entry) {
  const approx = entry.date_precision === "day" || entry.date_precision === "year" ? "" : "c. ";
  let text = approx + formatYear(entry.start);
  if (entry.end !== undefined && entry.end !== entry.start) text += " – " + approx + formatYear(entry.end);
  return text + (entry.disputed ? " (disputed)" : "");
}

export function link(url, text) {
  return '<a href="' + escapeHtml(url) + '" target="_blank" rel="noopener">' + text + "</a>";
}

export function sourceItem(src) {
  return "<li>" + (/^https?:\/\//.test(src) ? link(src, escapeHtml(src.replace(/^https?:\/\/(www\.)?/, ""))) : escapeHtml(src)) + "</li>";
}

export const fmtKm = (n) => n >= 1e6 ? (n / 1e6).toFixed(2) + " M km²" : Math.round(n).toLocaleString("en") + " km²";

// Fetch JSON, failing on HTTP errors.
export async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error("HTTP " + response.status);
  return response.json();
}
