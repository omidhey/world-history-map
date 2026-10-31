// Keeps the address bar in step with the view (year, followed country, layers, open card) and restores it.

import { state, polityById, enabled } from "./state.js";
import { CATEGORIES, snapshotFor } from "./categories.js";
import { encodeState, decodeState, snapshotIndexFor } from "./urlstate.js";
import { show } from "./main.js";
import { follow } from "./follow.js";
import { openCards, openPolityCard, closeCards, renderEntries } from "./panel.js";

const KEYS = CATEGORIES.map(([key]) => key);
let applying = true; // true until the first restore is done, so loading never overwrites the shared URL

function currentSearch() {
  const { snapshots, requested, followed, openIds, openPolity } = state;
  if (requested < 0) return "";
  return encodeState({
    year: snapshots[requested].year,
    country: followed,
    layers: enabled.size === KEYS.length ? null : KEYS.filter((k) => enabled.has(k)),
    entry: openIds && openIds.length === 1 ? openIds[0] : null,
    polity: openPolity ? openPolity.id : null,
  });
}

// `push` adds a history step (opening or closing a card, so Back works); otherwise the URL is replaced.
export function syncUrl(push = false) {
  if (applying) return;
  const search = currentSearch();
  if (search === location.search) return;
  try {
    history[push ? "pushState" : "replaceState"](null, "", location.pathname + search);
  } catch (error) { /* file:// or sandboxed frames */ }
}

// The year and layers can be applied as soon as the snapshots are known.
export function initialIndex(snapshots, fallback) {
  const wanted = decodeState(location.search, KEYS);
  if (wanted.layers) { enabled.clear(); wanted.layers.forEach((k) => enabled.add(k)); }
  return wanted.year !== undefined ? snapshotIndexFor(snapshots, wanted.year) : fallback;
}

// Country and cards need the data files; call once entries, polities and countries are loaded.
export async function restoreView() {
  await applyView(decodeState(location.search, KEYS), false);
  applying = false;
  syncUrl();
}

async function applyView(wanted, withYear) {
  applying = true;
  const { snapshots } = state;
  if (withYear || wanted.year !== undefined) {
    const i = wanted.year !== undefined ? snapshotIndexFor(snapshots, wanted.year) : state.requested;
    if (i !== state.requested) show(i);
  }
  const country = wanted.country && state.countryIndex[wanted.country] ? wanted.country : null;
  if (country !== state.followed) await follow(country);
  const entry = wanted.entry && state.entries.find((e) => e.id === wanted.entry);
  const polity = wanted.polity && polityById.get(wanted.polity);
  if (entry) {
    enabled.add(entry.category);
    const i = snapshotFor(entry, snapshots, state.requested);
    if (i !== state.requested) show(i);
    else renderEntries();
    openCards([entry.id], true);
  } else if (polity) {
    const i = snapshotFor({ start: polity.start, end: polity.end !== undefined ? polity.end : Infinity }, snapshots, state.requested);
    if (i !== state.requested) show(i);
    openPolityCard(polity, { NAME: polity.name, SUBJECTO: "" }, snapshots[i].year);
  } else if (state.openIds || state.openPolity) {
    closeCards();
  }
  applying = false;
}

// Back and Forward move between the cards and views that were pushed.
window.addEventListener("popstate", () => {
  const wanted = decodeState(location.search, KEYS);
  enabled.clear();
  (wanted.layers || KEYS).forEach((k) => enabled.add(k));
  renderEntries();
  applyView(wanted, true);
});

export function copyLink() {
  const button = document.getElementById("copy-link");
  const done = (text) => { button.textContent = text; setTimeout(() => { button.textContent = "Copy link"; }, 1500); };
  const search = currentSearch() || location.search;
  const url = location.origin + location.pathname + search;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(url).then(() => done("Copied"), () => { window.prompt("Copy this link", url); });
  } else {
    window.prompt("Copy this link", url);
  }
}
