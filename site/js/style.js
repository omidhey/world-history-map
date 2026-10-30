// How border polygons look and what their tooltips and popups say.

import { colourFor, escapeHtml, formatYear, suggestEditUrl } from "./util.js";
import { polityFor } from "./polities.js";

export function style(feature) {
  const p = feature.properties;
  const owner = p.SUBJECTO || p.NAME;
  const uncertain = p.BORDERPRECISION === 1;
  if (p.CARRIED !== undefined) {
    // Source has no realm here this year; keep the last recorded holder's colour, lighter (pipeline/carry_forward.py).
    return { color: "#777", weight: 0.4, opacity: 0.7, dashArray: "2 4",
             fillColor: colourFor(owner), fillOpacity: 0.35 };
  }
  if (p.OVERRIDE) {
    // Corrected by this project (data/borders/overrides.json): outlined so it is not mistaken for upstream data.
    return { color: "#6a2c91", weight: 1.6, opacity: 1, dashArray: "4 3",
             fillColor: colourFor(owner), fillOpacity: 0.7 };
  }
  return {
    color: "#444",
    weight: owner ? 0.8 : 0.4,
    opacity: uncertain ? 0.6 : 0.9,
    dashArray: uncertain ? "3 3" : null,
    fillColor: owner ? colourFor(owner) : "#e9e4d4", // unnamed land: neutral
    fillOpacity: owner ? (uncertain ? 0.55 : 0.8) : 0.6,
  };
}

export function tooltipHtml(p, year) {
  if (p.CARRIED !== undefined) {
    return "<small>Last recorded here (" + formatYear(p.CARRIED) + ")</small><br><b>" + escapeHtml(p.NAME) + "</b>" +
      '<div class="note">The source records no realm here in ' + formatYear(year) +
      ". The land keeps the colour of its last recorded holder; it may have ended or changed hands since.</div>";
  }
  let html = "<b>" + escapeHtml(p.NAME) + "</b>";
  if (p.SUBJECTO && p.SUBJECTO !== p.NAME) html += "<br><small>under " + escapeHtml(p.SUBJECTO) + "</small>";
  if (p.BORDERPRECISION === 1) html += "<br><small>border approximate</small>";
  if (p.OVERRIDE) {
    html += '<div class="note"><b>Corrected by this project.</b> ' + escapeHtml(p.NOTE) + "</div>";
  }
  if (polityFor(p, year)) html += "<br><small>click for details</small>";
  return html;
}

export function popupHtml(p, year) {
  const name = p.NAME || "unnamed land";
  const url = suggestEditUrl("border-error.yml", "[Border] " + name + ", " + formatYear(year), {
    year: formatYear(year),
    realm: p.SUBJECTO && p.SUBJECTO !== p.NAME ? name + " (under " + p.SUBJECTO + ")" : name,
  });
  return "<b>" + escapeHtml(name) + "</b><br><small>Borders as of " + formatYear(year) + "</small><br>" +
    '<a href="' + escapeHtml(url) + '" target="_blank" rel="noopener">Report a border error</a>';
}

export function highlight(event) {
  event.target.setStyle({ weight: 2.5, color: "#000", opacity: 1 });
  event.target.bringToFront();
}
