// Side panel (category toggles with the period's entries, or the open card) and the entry markers.

import { state, polityById, enabled } from "./state.js";
import { map, entriesLayer } from "./map.js";
import { CATEGORIES, categoryColour, inPeriod, periodOf } from "./categories.js";
import { escapeHtml, formatDates, formatYear, getJson } from "./util.js";
import { cardHtml, polityCardHtml } from "./cards.js";
import { renderTimeline } from "./rulers.js";
import { follow, followHtml } from "./follow.js";
import { show } from "./main.js";

const panel = document.getElementById("panel");
const markerById = new Map();
let highlighted = [];

function setHighlight(ids) {
  for (const marker of highlighted) marker.setStyle({ color: "#fff", weight: 2 });
  highlighted = [];
  for (const id of ids || []) {
    const marker = markerById.get(id);
    if (!marker) continue;
    marker.setStyle({ color: "#000", weight: 4 });
    marker.bringToFront();
    highlighted.push(marker);
  }
}

export function openPolityCard(polity, props, year) {
  state.openPolity = { id: polity.id, props: { NAME: props.NAME, SUBJECTO: props.SUBJECTO }, year };
  state.openIds = null;
  panel.classList.remove("sheet-closed");
  renderPanel();
  renderEntries();
}

export function openCards(ids, centre) {
  state.openPolity = null;
  state.openIds = ids;
  const first = state.entries.find((e) => e.id === ids[0]);
  if (centre && first) map.setView([first.location.lat, first.location.lon], Math.max(map.getZoom(), 4));
  panel.classList.remove("sheet-closed");
  renderPanel();
}

export function closeCards() {
  state.openIds = null;
  state.openPolity = null;
  renderPanel();
  renderEntries();
}

export function renderPanel() {
  const { snapshots, requested, openPolity, openIds, currentList, entries } = state;
  if (!snapshots.length || requested < 0) return;
  renderTimeline();
  const period = periodOf(snapshots, requested);
  if (openPolity) {
    panel.innerHTML = '<header><button class="back">← All entries</button></header>' +
      polityCardHtml(polityById.get(openPolity.id), openPolity.props, openPolity.year);
    panel.querySelector(".back").addEventListener("click", closeCards);
    setHighlight([]);
    return;
  }
  if (openIds) {
    const shown = openIds.map((id) => entries.find((e) => e.id === id)).filter(Boolean);
    panel.innerHTML = '<header><button class="back">← All entries</button></header>' + shown.map(cardHtml).join("");
    panel.querySelector(".back").addEventListener("click", closeCards);
    setHighlight(openIds);
    return;
  }
  panel.innerHTML = followHtml(snapshots[requested].year) + '<header><b>In this period</b> <span class="count">' + currentList.length + '</span><div class="period">' +
    formatYear(period.from) + " – " + formatYear(period.to) + "</div></header>" +
    CATEGORIES.map(([key, label, colour]) => {
      const items = currentList.filter((e) => e.category === key);
      return '<label class="cat' + (items.length ? "" : " empty") + '"><input type="checkbox" value="' + key + '"' +
        (enabled.has(key) ? " checked" : "") + '><span class="dot" style="background:' + colour + '"></span>' + label +
        '<span class="count">' + items.length + "</span></label>" +
        (enabled.has(key) ? items.map((e) =>
          '<button class="item-btn" data-id="' + escapeHtml(e.id) + '"><b>' + escapeHtml(e.name) + "</b><small>" +
          escapeHtml(formatDates(e)) + "</small></button>").join("") : "");
    }).join("");
  setHighlight([]);
}

export function renderEntries() {
  entriesLayer.clearLayers();
  markerById.clear();
  highlighted = [];
  if (state.requested < 0 || !state.snapshots.length) return;
  state.currentList = state.entries.filter((e) => inPeriod(e, periodOf(state.snapshots, state.requested)))
    .sort((a, b) => a.start - b.start || a.id.localeCompare(b.id));
  if (state.openIds) state.openIds = state.openIds.filter((id) => state.currentList.some((e) => e.id === id));
  if (state.openIds && !state.openIds.length) state.openIds = null;

  // One marker per place, so records at the same spot (e.g. Athens) stay clickable.
  const byPlace = new Map();
  for (const entry of state.currentList) {
    if (!enabled.has(entry.category)) continue;
    const key = entry.location.lat + "," + entry.location.lon;
    if (!byPlace.has(key)) byPlace.set(key, []);
    byPlace.get(key).push(entry);
  }
  for (const group of byPlace.values()) {
    const first = group[0];
    const marker = L.circleMarker([first.location.lat, first.location.lon], {
      pane: "entries", radius: group.length > 1 ? 8 : 6,
      color: "#fff", weight: 2, opacity: 1, fillColor: categoryColour[first.category], fillOpacity: 1,
    });
    marker.bindTooltip(
      group.map((e) => "<b>" + escapeHtml(e.name) + "</b> <small>" + escapeHtml(formatDates(e)) + "</small>").join("<br>"),
      { className: "entry", direction: "top", offset: [0, -6] }
    );
    const ids = group.map((e) => e.id);
    marker.on("click", () => openCards(ids, false));
    group.forEach((e) => markerById.set(e.id, marker));
    entriesLayer.addLayer(marker);
  }
  renderPanel();
}

export function loadEntries() {
  getJson("data/entries.json")
    .then((data) => {
      state.entries = data;
      renderEntries();
    })
    .catch((error) => {
      panel.textContent = "Could not load entries (" + error.message + ")";
    });
}

panel.addEventListener("change", (e) => {
  if (e.target.id === "follow") { follow(e.target.value); return; }
  if (e.target.checked) enabled.add(e.target.value);
  else enabled.delete(e.target.value);
  renderEntries();
});
panel.addEventListener("click", (e) => {
  if (e.target.closest(".stop")) { follow(null); return; }
  const pt = e.target.closest("circle[data-year]");
  if (pt) {
    const i = state.snapshots.findIndex((s) => s.year === Number(pt.dataset.year));
    if (i >= 0 && i !== state.requested) show(i);
    return;
  }
  const power = e.target.closest("[data-polity]");
  if (power) {
    openPolityCard(polityById.get(power.dataset.polity), { NAME: power.dataset.name, SUBJECTO: power.dataset.subjecto }, state.snapshots[state.requested].year);
    return;
  }
  const btn = e.target.closest(".item-btn");
  if (btn) openCards([btn.dataset.id], true);
  else if (window.innerWidth <= 600 && e.target.closest("header") && !e.target.closest(".back")) {
    panel.classList.toggle("sheet-closed");
  }
});
document.addEventListener("keydown", (e) => { if (e.key === "Escape" && (state.openIds || state.openPolity)) closeCards(); });
document.getElementById("panel-toggle").addEventListener("click", () => {
  panel.classList.toggle("collapsed");
  map.invalidateSize();
});
if (window.innerWidth <= 600) panel.classList.add("sheet-closed");
