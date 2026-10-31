// Fuzzy search over entries and states (Fuse.js, vendored in site/vendor/fuse/). No DOM, so it can be tested.

import Fuse from "../vendor/fuse/fuse.min.mjs";

export function buildIndex(entries, polities) {
  const docs = [
    ...entries.map((e) => ({ kind: "entry", id: e.id, name: e.name, place: e.location.place, summary: e.summary, ref: e })),
    ...polities.map((p) => ({ kind: "polity", id: p.id, name: p.name, place: p.capital ? p.capital.place : "", summary: p.summary, ref: p })),
  ];
  return new Fuse(docs, {
    keys: [{ name: "name", weight: 3 }, { name: "place", weight: 1 }, { name: "summary", weight: 0.3 }],
    threshold: 0.3, ignoreLocation: true, minMatchCharLength: 2,
  });
}

export function search(index, query, limit = 20) {
  const text = query.trim();
  return text.length < 2 ? [] : index.search(text, { limit }).map((r) => r.item);
}
