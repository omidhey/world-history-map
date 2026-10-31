// Entry point: loads the data, owns the slider and the border layer, and wires the modules together.

import { state } from "./state.js";
import { map } from "./map.js";
import { formatYear, getJson } from "./util.js";
import { style, tooltipHtml, popupHtml, highlight } from "./style.js";
import { loadPolities, polityFor } from "./polities.js";
import { loadRulers } from "./rulers.js";
import { loadAreas } from "./areas.js";
import { loadCountries } from "./follow.js";
import { loadEntries, openPolityCard, renderEntries } from "./panel.js";
import { initialIndex, restoreView, syncUrl } from "./view.js";
import "./search.js";

const DATA = "data/borders/";
const titleEl = document.getElementById("title");
const slider = document.getElementById("slider");
const ticksEl = document.getElementById("ticks");

let currentLayer = null;
const cache = new Map(); // year -> Promise<GeoJSON> (files are TopoJSON; converted once on load)

function loadYear(year, file) {
  if (!cache.has(year)) {
    const request = getJson(DATA + file).then((topology) => topojson.feature(topology, Object.values(topology.objects)[0]));
    request.catch(() => cache.delete(year)); // allow a retry after a failed load
    cache.set(year, request);
  }
  return cache.get(year);
}

export async function show(index) {
  const { snapshots } = state;
  state.requested = index;
  const { year, file } = snapshots[index];
  slider.value = index;
  titleEl.textContent = "Borders as of " + formatYear(year) + " …";
  renderEntries();
  syncUrl();
  ticksEl.querySelectorAll("span").forEach((s, i) => s.classList.toggle("current", i === index));

  let geojson;
  try {
    geojson = await loadYear(year, file);
  } catch (error) {
    titleEl.textContent = "Could not load " + formatYear(year) + " (" + error.message + ")";
    return;
  }
  await politiesReady; // never rejects; polity cards just stay off if the file is missing
  if (state.requested !== index) return; // the slider moved on while this file was loading

  const layer = L.geoJSON(geojson, {
    style,
    onEachFeature: (feature, layer) => {
      const polity = polityFor(feature.properties, year);
      if (polity) layer.on("click", () => openPolityCard(polity, feature.properties, year));
      else layer.bindPopup(popupHtml(feature.properties, year), { className: "polity" });
      if (!feature.properties.NAME) return; // unnamed land: no tooltip
      layer.bindTooltip(tooltipHtml(feature.properties, year), { sticky: true, className: "polity" });
      layer.on({ mouseover: highlight, mouseout: (e) => layer.setStyle(style(feature)) });
    },
  }).addTo(map);
  if (currentLayer) map.removeLayer(currentLayer);
  currentLayer = layer;
  titleEl.textContent = "Borders as of " + formatYear(year);

  // Warm the cache for the neighbours so sliding feels instant.
  for (const n of [index - 1, index + 1]) {
    if (snapshots[n]) loadYear(snapshots[n].year, snapshots[n].file).catch(() => {});
  }
}

function step(delta) {
  const index = Math.min(state.snapshots.length - 1, Math.max(0, Number(slider.value) + delta));
  if (index !== state.requested) show(index);
}

slider.addEventListener("input", () => show(Number(slider.value)));
document.getElementById("prev").addEventListener("click", () => step(-1));
document.getElementById("next").addEventListener("click", () => step(1));
document.addEventListener("keydown", (e) => {
  if (e.target === slider) return; // the range input handles its own arrow keys
  if (e.key === "ArrowLeft") step(-1);
  if (e.key === "ArrowRight") step(1);
});

const countriesReady = loadCountries();
const entriesReady = loadEntries();
loadRulers();
loadAreas();
const politiesReady = loadPolities();

getJson(DATA + "manifest.json")
  .then((manifest) => {
    state.snapshots = manifest.snapshots;
    slider.max = state.snapshots.length - 1;
    state.snapshots.forEach(({ year }, i) => {
      const tick = document.createElement("span");
      tick.textContent = year < 0 ? -year + " BCE" : year;
      tick.addEventListener("click", () => show(i));
      ticksEl.appendChild(tick);
    });
    const start = state.snapshots.findIndex((s) => s.year === 1500);
    show(initialIndex(state.snapshots, start >= 0 ? start : 0));
    return Promise.all([entriesReady, politiesReady, countriesReady]).then(restoreView);
  })
  .catch((error) => {
    titleEl.textContent =
      "Could not load borders (" + error.message + "). Run pipeline/build_site.py, then start the page with run_site.bat.";
  });
