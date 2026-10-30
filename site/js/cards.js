// HTML for the info cards: one entry, or one state.

import { SINGULAR } from "./categories.js";
import { REPO, escapeHtml, formatDates, formatYear, link, sourceItem, suggestEditUrl } from "./util.js";
import { areaHtml } from "./areas.js";
import { reignsHtml } from "./rulers.js";

export function cardHtml(entry) {
  const edit = suggestEditUrl("correct-entry.yml", "[Correction] " + entry.id, { entry: entry.id });
  let html = '<div class="card"><h2>' + escapeHtml(entry.name) + "</h2><small>" +
    SINGULAR[entry.category] + " · " + escapeHtml(formatDates(entry)) + " · " +
    escapeHtml(entry.location.place) + "</small><p>" + escapeHtml(entry.summary) + "</p>";
  if (entry.claims) {
    html += '<div class="disputed"><b>Disputed.</b> Sources disagree:<ul>' + entry.claims.map((c) =>
      "<li>" + c.field + ": " + formatYear(c.value) + (c.note ? " — " + escapeHtml(c.note) : "") + "</li>").join("") + "</ul></div>";
  }
  if (entry.links && entry.links.wikipedia) html += "<p>" + link(entry.links.wikipedia, "Wikipedia") + "</p>";
  html += "<b>Sources</b><ul>" + (entry.sources || []).map(sourceItem).join("") + "</ul><small>" +
    link(REPO + "/blob/main/data/entries/" + encodeURIComponent(entry.id) + ".json", "View record on GitHub") +
    '</small><br><a class="edit" href="' + escapeHtml(edit) + '" target="_blank" rel="noopener">Suggest an edit</a></div>';
  return html;
}

export function polityCardHtml(polity, p, year) {
  const edit = suggestEditUrl("correct-entry.yml", "[Correction] polity " + polity.id, { entry: polity.id });
  const border = suggestEditUrl("border-error.yml", "[Border] " + polity.name + ", " + formatYear(year), {
    year: formatYear(year), realm: polity.name });
  let html = '<div class="card"><h2>' + escapeHtml(polity.name) + "</h2><small>" +
    polity.type.charAt(0).toUpperCase() + polity.type.slice(1) + " · " + escapeHtml(formatDates(polity)) +
    (polity.capital ? " · capital " + escapeHtml(polity.capital.place) : "") + "</small>";
  if (p.NAME !== polity.name) {
    html += "<br><small>Shown on the map as “" + escapeHtml(p.NAME || p.SUBJECTO) + "”</small>";
  }
  html += "<p>" + escapeHtml(polity.summary) + "</p>";
  if (polity.claims) {
    html += '<div class="disputed"><b>Disputed.</b> Sources disagree:<ul>' + polity.claims.map((c) =>
      "<li>" + c.field + ": " + formatYear(c.value) + (c.note ? " — " + escapeHtml(c.note) : "") + "</li>").join("") + "</ul></div>";
  }
  html += areaHtml(polity);
  html += reignsHtml(polity, year);
  if (polity.links && polity.links.wikipedia) html += "<p>" + link(polity.links.wikipedia, "Wikipedia") + "</p>";
  html += "<b>Sources</b><ul>" + (polity.sources || []).map(sourceItem).join("") + "</ul><small>" +
    link(REPO + "/blob/main/data/polities/" + encodeURIComponent(polity.id) + ".json", "View record on GitHub") +
    '</small><br><a class="edit" href="' + escapeHtml(edit) + '" target="_blank" rel="noopener">Suggest an edit</a>' +
    ' · <a class="edit" href="' + escapeHtml(border) + '" target="_blank" rel="noopener">Report a border error</a>' +
    "<br><small>Borders as of " + formatYear(year) + " are approximate.</small></div>";
  return html;
}
