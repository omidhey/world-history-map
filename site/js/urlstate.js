// View state in the URL (?year=-500&country=IRN&layers=philosopher,writer&entry=socrates). Pure.

const ID = /^[A-Za-z0-9_.-]{1,100}$/;

// Latest snapshot at or before `year`; before the first snapshot, the first one. -1 for no snapshots.
export function snapshotIndexFor(snapshots, year) {
  let index = snapshots.length ? 0 : -1;
  snapshots.forEach((s, i) => { if (s.year <= year) index = i; });
  return index;
}

// `layers`: array of enabled category keys, or null when all are on. Empty values are left out.
export function encodeState({ year, country, layers, entry, polity }) {
  const params = new URLSearchParams();
  if (Number.isInteger(year)) params.set("year", String(year));
  if (country) params.set("country", country);
  if (layers) params.set("layers", layers.join(","));
  if (entry) params.set("entry", entry);
  else if (polity) params.set("polity", polity);
  const text = params.toString().replace(/%2C/g, ",");
  return text ? "?" + text : "";
}

// Returns only the fields that are present and well-formed; anything else is ignored.
// `categories` is the list of known category keys.
export function decodeState(search, categories) {
  const params = new URLSearchParams(search);
  const out = {};
  const year = params.get("year");
  if (year !== null && /^-?\d{1,5}$/.test(year) && Number(year) !== 0) out.year = Number(year);
  const country = params.get("country");
  if (country && /^[A-Z0-9]{2,4}$/.test(country)) out.country = country;
  const layers = params.get("layers");
  if (layers !== null) {
    const known = layers.split(",").filter((key) => categories.includes(key));
    if (known.length || layers === "") out.layers = [...new Set(known)];
  }
  const entry = params.get("entry");
  const polity = params.get("polity");
  if (entry && ID.test(entry)) out.entry = entry;
  else if (polity && ID.test(polity)) out.polity = polity;
  return out;
}
