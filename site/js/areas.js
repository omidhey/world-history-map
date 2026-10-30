// Territory over time (data/areas/areas.json, made by pipeline/make_areas.py).

import { state } from "./state.js";
import { escapeHtml, fmtKm, formatYear, getJson } from "./util.js";
import { renderPanel } from "./panel.js";

export function loadAreas() {
  getJson("data/areas.json")
    .then((data) => { state.areaData = data; if (state.openPolity) renderPanel(); })
    .catch((error) => console.warn("Could not load areas (" + error.message + ")"));
}

export function areaHtml(polity) {
  const series = state.areaData[polity.id];
  const years = series ? Object.keys(series).map(Number).sort((a, b) => a - b) : [];
  if (years.length < 2) return "";
  const now = state.snapshots[state.requested].year;
  const W = 300, H = 120, L = 6, R = 6, T = 8, B = 18;
  const total = (y) => series[y].area_km2 + series[y].carried_km2;
  const max = Math.max(...years.map(total), 1);
  const lo = years[0], span = Math.max(1, years[years.length - 1] - lo);
  const px = (y) => L + ((y - lo) / span) * (W - L - R);
  const py = (v) => T + (1 - v / max) * (H - T - B);
  const line = (f) => years.map((y, i) => (i ? "L" : "M") + px(y).toFixed(1) + " " + py(f(y)).toFixed(1)).join(" ");
  let svg = '<svg class="area" viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="Territory of ' + escapeHtml(polity.name) + ' by snapshot">' +
    '<path d="' + line(total) + '" class="carried"/><path d="' + line((y) => series[y].area_km2) + '" class="recorded"/>';
  for (const y of years) {
    svg += '<circle data-year="' + y + '" class="pt' + (y === now ? " now" : "") + '" cx="' + px(y).toFixed(1) + '" cy="' + py(series[y].area_km2).toFixed(1) +
      '" r="4"><title>' + escapeHtml(formatYear(y) + ": " + fmtKm(series[y].area_km2) + (series[y].carried_km2 ? " + " + fmtKm(series[y].carried_km2) + " last recorded" : "")) + "</title></circle>";
  }
  svg += '<text x="' + L + '" y="' + (H - 4) + '">' + formatYear(years[0]) + '</text><text x="' + (W - R) + '" y="' + (H - 4) + '" text-anchor="end">' +
    formatYear(years[years.length - 1]) + '</text><text x="' + L + '" y="8">' + fmtKm(max) + "</text></svg>";
  const cur = series[now];
  let change = "";
  if (cur) {
    change = fmtKm(cur.area_km2) + " in " + formatYear(now) + (cur.carried_km2 ? " (+ " + fmtKm(cur.carried_km2) + " last recorded)" : "");
    if (cur.gained_km2 !== undefined) change += ". Since the previous snapshot: +" + fmtKm(cur.gained_km2) + ", −" + fmtKm(cur.lost_km2) + ".";
  } else change = "Not on the map in " + formatYear(now) + ".";
  return '<details open><summary>Territory over time</summary>' + svg + "<small>" + change +
    " Click a point to go to that snapshot. Areas are approximate; a state that split is shown as lost land.</small></details>";
}
