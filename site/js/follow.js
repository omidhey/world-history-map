// Follow a country (data/lineage/<ISO>.json, outlines in countries.json).

import { state } from "./state.js";
import { map } from "./map.js";
import { colourFor, escapeHtml, formatYear, getJson } from "./util.js";
import { polityFor } from "./polities.js";
import { closeCards, renderPanel } from "./panel.js";

const lineageCache = new Map();

export function loadCountries() {
  getJson("data/lineage/index.json")
    .then((d) => { state.countryIndex = d; if (!state.openIds && !state.openPolity) renderPanel(); })
    .catch(() => {});
  getJson("data/countries.json")
    .then((d) => { for (const f of d.features) state.countryShapes[f.properties.iso] = f; })
    .catch(() => {});
}

export async function follow(iso) {
  state.followed = iso || null;
  state.followData = null;
  if (state.followLayer) { map.removeLayer(state.followLayer); state.followLayer = null; }
  if (state.followed) {
    const wanted = state.followed;
    try {
      if (!lineageCache.has(wanted)) lineageCache.set(wanted, getJson("data/lineage/" + wanted + ".json"));
      state.followData = await lineageCache.get(wanted);
    } catch (error) {
      lineageCache.delete(wanted);
      state.followed = null;
    }
    if (state.followed !== wanted) { renderPanel(); return; }
    const shape = state.countryShapes[wanted];
    if (shape) {
      state.followLayer = L.geoJSON(shape, { interactive: false, style: { color: "#111", weight: 3, fill: false } }).addTo(map);
      state.followLayer.bringToFront();
      map.fitBounds(state.followLayer.getBounds(), { maxZoom: 6, padding: [30, 30] });
    }
  }
  closeCards();
}

export function followHtml(year) {
  const { followed, followData, countryIndex, snapshots, requested } = state;
  let options = '<option value="">None</option>' + Object.entries(countryIndex)
    .sort((a, b) => a[1].name.localeCompare(b[1].name))
    .map(([iso, c]) => '<option value="' + iso + '"' + (iso === followed ? " selected" : "") + ">" + escapeHtml(c.name) + (c.curated ? " ★" : "") + "</option>").join("");
  let html = '<div class="follow">' + (followed ? '<button class="stop">Stop</button>' : "") +
    "<b>Follow a country</b><select id=\"follow\" aria-label=\"Follow a country\">" + options + "</select>";
  const snap = followData && followData.snapshots[String(snapshots[requested].year)];
  if (snap) {
    html += "<small>Who held " + escapeHtml(followData.name) + " as of " + formatYear(snapshots[requested].year) + ":</small>";
    for (const s of snap) {
      const label = s.other ? "Other (small shares)" : s.name || "Unnamed land";
      const pct = (s.share * 100 < 1 ? "<1" : Math.round(s.share * 100)) + " %";
      const polity = s.name ? polityFor({ NAME: s.name, SUBJECTO: s.subjecto }, year) : null;
      const tag = polity ? "button" : "div";
      html += "<" + tag + ' class="power"' + (polity ? ' data-polity="' + escapeHtml(polity.id) + '" data-name="' + escapeHtml(s.name) + '" data-subjecto="' + escapeHtml(s.subjecto || "") + '"' : "") + ">" +
        escapeHtml(label) + '<span style="float:right">' + pct + '</span><span class="bar" style="width:' + Math.max(2, s.share * 100) +
        "%;background:" + (s.other || !s.name ? "#bbb" : colourFor(s.subjecto || s.name)) + '"></span></' + tag + ">";
    }
    const note = followData.notes && followData.notes[String(snapshots[requested].year)];
    if (note) html += "<small>" + escapeHtml(note) + "</small>";
    if (followData.source === "automatic") {
      html += "<small>Automatic area match against simplified borders; approximate.</small>";
    } else {
      if (followData.note) html += "<small>" + escapeHtml(followData.note) + "</small>";
      html += "<small>★ Curated: holders chosen by hand, shares from the area match. Notes are unreviewed.</small>" +
        "<details><summary>Sources</summary><ul>" + (followData.sources || []).map((u) =>
          '<li><a href="' + escapeHtml(u) + '" target="_blank" rel="noopener">' + escapeHtml(u.replace(/^https?:\/\//, "")) + "</a></li>").join("") + "</ul></details>";
    }
  }
  return html + "</div>";
}
