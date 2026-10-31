// Search box above the side panel: results drop down over the panel; choosing one jumps to its period and opens its card.

import { state, polityById, enabled } from "./state.js";
import { categoryColour, snapshotFor } from "./categories.js";
import { escapeHtml, formatDates } from "./util.js";
import { buildIndex, search } from "./searchindex.js";
import { openCards, openPolityCard, renderEntries } from "./panel.js";
import { show } from "./main.js";
import { copyLink } from "./view.js";

const input = document.getElementById("search");
const list = document.getElementById("search-results");
let index = null, indexKey = "", hits = [], active = -1;

function indexFor() {
  const key = state.entries.length + ":" + polityById.size;
  if (key !== indexKey) {
    index = buildIndex(state.entries, [...polityById.values()]);
    indexKey = key;
  }
  return index;
}

function render() {
  list.hidden = !input.value.trim();
  if (list.hidden) return;
  if (!state.entries.length) { list.innerHTML = '<div class="none">Loading entries…</div>'; return; }
  hits = search(indexFor(), input.value);
  active = hits.length ? 0 : -1;
  list.innerHTML = hits.length ? hits.map((h, i) => {
    const colour = h.kind === "entry" ? categoryColour[h.ref.category] : "#888";
    const dates = escapeHtml(formatDates(h.ref));
    return '<button type="button" role="option" data-i="' + i + '"' + (i === active ? ' class="active"' : "") +
      '><span class="dot" style="background:' + colour + '"></span><b>' + escapeHtml(h.name) + "</b><small>" +
      (h.kind === "polity" ? "State · " : "") + dates + (h.place ? " · " + escapeHtml(h.place) : "") + "</small></button>";
  }).join("") : '<div class="none">No match</div>';
}

function setActive(i) {
  active = (i + hits.length) % hits.length;
  list.querySelectorAll("button").forEach((b, n) => b.classList.toggle("active", n === active));
  const el = list.querySelector("button.active");
  if (el) el.scrollIntoView({ block: "nearest" });
}

function clear() {
  input.value = "";
  list.hidden = true;
  hits = [];
}

function pick(hit) {
  clear();
  document.getElementById("panel").classList.remove("collapsed");
  if (hit.kind === "entry") {
    const entry = hit.ref;
    enabled.add(entry.category);
    const i = snapshotFor(entry, state.snapshots, state.requested);
    if (i !== state.requested) show(i); // renders the entries for the new period before the first await
    else renderEntries();
    openCards([entry.id], true);
  } else {
    const polity = hit.ref;
    const i = snapshotFor({ start: polity.start, end: polity.end !== undefined ? polity.end : Infinity }, state.snapshots, state.requested);
    if (i !== state.requested) show(i);
    openPolityCard(polity, { NAME: polity.name, SUBJECTO: "" }, state.snapshots[i].year);
  }
}

input.addEventListener("input", render);
input.addEventListener("keydown", (e) => {
  if (e.key === "Escape") { clear(); input.blur(); e.stopPropagation(); }
  else if (e.key === "ArrowDown" && hits.length) { e.preventDefault(); setActive(active + 1); }
  else if (e.key === "ArrowUp" && hits.length) { e.preventDefault(); setActive(active - 1); }
  else if (e.key === "Enter" && hits[active]) pick(hits[active]);
  else if (e.key === "ArrowLeft" || e.key === "ArrowRight") e.stopPropagation(); // do not step the slider while typing
});
list.addEventListener("click", (e) => {
  const button = e.target.closest("button[data-i]");
  if (button) pick(hits[Number(button.dataset.i)]);
});
document.addEventListener("click", (e) => { if (!e.target.closest("#search-bar")) list.hidden = true; });
input.addEventListener("focus", () => { if (input.value.trim()) render(); });
document.getElementById("copy-link").addEventListener("click", copyLink);
