// The Leaflet map. `L` is the global from the classic vendor/leaflet script.

export const map = L.map("map", { worldCopyJump: true, preferCanvas: true }).setView([30, 20], 2);
map.attributionControl.setPrefix(false); // credits live in the footer

map.createPane("entries").style.zIndex = 450; // above the border polygons, below tooltips and popups
export const entriesLayer = L.layerGroup().addTo(map);
