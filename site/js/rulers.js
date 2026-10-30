// Dynasties and rulers (data/dynasties + data/rulers merged into data/rulers.json), and the
// timeline strip under the map: the open state's dynasties and rulers with a marker at the slider's year.

import { state, polityById } from "./state.js";
import { map } from "./map.js";
import { escapeHtml, formatDates, formatYear, getJson, link } from "./util.js";
import { renderPanel } from "./panel.js";
import { show } from "./main.js";

const timelineEl = document.getElementById("timeline");

export function loadRulers() {
  getJson("data/rulers.json")
    .then((data) => { state.rulerData = data; if (state.openPolity) renderPanel(); })
    .catch((error) => console.warn("Could not load rulers (" + error.message + ")"));
}

export function reignsHtml(polity, year) {
  const group = state.rulerData[polity.id];
  if (!group) return "";
  const reigning = (r) => r.start <= year && year <= (r.end !== undefined ? r.end : r.start);
  const item = (r, extra) => '<li' + (reigning(r) ? ' class="now"' : "") + ">" +
    (r.links && r.links.wikipedia ? link(r.links.wikipedia, escapeHtml(r.name)) : escapeHtml(r.name)) +
    '<small>' + (extra ? escapeHtml(extra) + " · " : "") + escapeHtml(formatDates(r)) + (reigning(r) ? " · in power in " + formatYear(year) : "") + "</small></li>";
  const dynastyName = new Map(group.dynasties.map((d) => [d.id, d.name]));
  let html = "";
  if (group.dynasties.length) {
    html += '<details open><summary>Dynasties (' + group.dynasties.length + ')</summary><ul class="reigns">' +
      group.dynasties.map((d) => item(d, "")).join("") + "</ul></details>";
  }
  if (group.rulers.length) {
    html += '<details' + (group.rulers.length <= 10 ? " open" : "") + '><summary>Rulers (' + group.rulers.length + ')</summary><ul class="reigns">' +
      group.rulers.map((r) => item(r, [r.title, r.dynasty && dynastyName.get(r.dynasty)].filter(Boolean).join(", "))).join("") +
      "</ul><small>A selection, not every ruler. Reign years follow the conventional chronology.</small></details>";
  }
  return html;
}

export function renderTimeline() {
  const { openPolity, rulerData, requested, snapshots } = state;
  const group = openPolity && rulerData[openPolity.id];
  if (!group || requested < 0 || !(group.dynasties.length || group.rulers.length)) { timelineEl.hidden = true; return; }
  const polity = polityById.get(openPolity.id);
  const year = snapshots[requested].year;
  const endOf = (r) => (r.end !== undefined ? r.end : r.start);
  const all = group.dynasties.concat(group.rulers);
  const lo = Math.min(polity.start, ...all.map((r) => r.start));
  const hi = Math.max(polity.end !== undefined ? polity.end : -Infinity, ...all.map(endOf));
  const span = Math.max(1, hi - lo);
  timelineEl.hidden = false;
  const width = Math.max(200, timelineEl.clientWidth - 32);
  const x = (y) => Math.min(width, Math.max(0, ((y - lo) / span) * width));
  const reigning = (r) => r.start <= year && year <= endOf(r);

  // Dynasties that overlap in time go on separate rows.
  const laneEnds = [];
  const dynasties = group.dynasties.slice().sort((a, b) => a.start - b.start).map((d) => {
    let lane = laneEnds.findIndex((end) => end < d.start);
    if (lane < 0) lane = laneEnds.length;
    laneEnds[lane] = endOf(d);
    return { d, lane };
  });
  const LANE = 14, top = 16;
  const rulerY = top + Math.max(1, laneEnds.length) * LANE + 4;
  const height = rulerY + 12 + 14;
  const bar = (r, cls, y, h) => '<rect class="' + cls + (reigning(r) ? " now" : "") + '" data-year="' + r.start + '" x="' + x(r.start).toFixed(1) +
    '" y="' + y + '" width="' + Math.max(2, x(endOf(r)) - x(r.start)).toFixed(1) + '" height="' + h + '"><title>' +
    escapeHtml(r.name + " · " + formatDates(r)) + "</title></rect>";
  const now = all.filter(reigning).filter((r) => group.rulers.includes(r));
  const who = now.length ? now.map((r) => r.name).join(", ") : "no ruler recorded";
  const mx = x(year);
  const anchor = mx > width - 160 ? "end" : "start";
  let svg = '<svg height="' + height + '" width="' + width + '">' +
    dynasties.map(({ d, lane }) => bar(d, "dyn", top + lane * LANE, LANE - 2)).join("") +
    group.rulers.map((r) => bar(r, "rul", rulerY, 10)).join("") +
    '<line class="marker" x1="' + mx + '" x2="' + mx + '" y1="0" y2="' + (rulerY + 12) + '"/>' +
    '<text x="' + (anchor === "end" ? mx - 4 : mx + 4) + '" y="10" text-anchor="' + anchor + '">' +
    escapeHtml(formatYear(year) + ": " + who) + "</text>" +
    '<text x="0" y="' + (height - 3) + '">' + formatYear(lo) + '</text><text x="' + width + '" y="' + (height - 3) +
    '" text-anchor="end">' + formatYear(hi) + "</text></svg>";
  timelineEl.innerHTML = svg;
  timelineEl.setAttribute("aria-label", "Timeline of " + polity.name + ". " + formatYear(year) + ": " + who);
  map.invalidateSize();
}

timelineEl.addEventListener("click", (e) => {
  const bar = e.target.closest("[data-year]");
  if (!bar) return;
  const { snapshots, requested } = state;
  const target = Number(bar.dataset.year);
  let best = 0;
  snapshots.forEach((s, i) => { if (Math.abs(s.year - target) < Math.abs(snapshots[best].year - target)) best = i; });
  if (best !== requested) show(best);
});
window.addEventListener("resize", renderTimeline);
