// Entry categories, and the period logic that decides which entries show at a snapshot (pure).

// Fixed category order and colours (validated categorical palette; filtering never repaints).
export const CATEGORIES = [
  ["philosopher", "Philosophers", "#2a78d6"],
  ["scientist", "Scientists", "#eb6834"],
  ["writer", "Writers", "#1baf7a"],
  ["work", "Works", "#eda100"],
  ["invention", "Inventions", "#e87ba4"],
  ["ruler", "Rulers", "#008300"],
  ["dynasty", "Dynasties", "#6250d6"],
  ["culture", "Cultures", "#e34948"],
  ["event", "Environmental events", "#7a5c3e"],
];
export const SINGULAR = { philosopher: "Philosopher", scientist: "Scientist", writer: "Writer", work: "Work",
                          invention: "Invention", ruler: "Ruler", dynasty: "Dynasty", culture: "Culture", event: "Environmental event" };
export const categoryColour = Object.fromEntries(CATEGORIES.map(([key, , colour]) => [key, colour]));

// The period a snapshot stands for: from its year up to the year before the next snapshot.
export function periodOf(snapshots, index, thisYear = new Date().getFullYear()) {
  const from = snapshots[index].year;
  const next = snapshots[index + 1];
  let to = next ? next.year - 1 : thisYear;
  if (to === 0) to = -1; // there is no year 0
  return { from, to };
}

// People, dynasties and cultures show while they lived or lasted; works and inventions
// without an end year show in the period they appeared. Disputed records use the
// widest range of their competing claims (span, from pipeline/build.py).
export function inPeriod(entry, { from, to }) {
  const [start, end] = entry.span || [entry.start, entry.end !== undefined ? entry.end : entry.start];
  return start <= to && end >= from;
}

// The snapshot to jump to so `range` ({start, end?, span?}) is in view: the current one if it
// already is, else the nearest snapshot whose period overlaps it, else the latest one before it.
export function snapshotFor(range, snapshots, current) {
  let best = -1;
  snapshots.forEach((_, i) => {
    if (!inPeriod(range, periodOf(snapshots, i))) return;
    if (best < 0 || Math.abs(i - current) < Math.abs(best - current)) best = i;
  });
  if (best >= 0) return best;
  const start = range.span ? range.span[0] : range.start;
  let before = 0;
  snapshots.forEach((s, i) => { if (s.year <= start) before = i; });
  return before;
}
