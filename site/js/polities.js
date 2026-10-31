// Polities (data/polities/ merged into data/polities.json by pipeline/build.py).

import { state, polityById } from "./state.js";
import { getJson } from "./util.js";

// A border NAME can belong to different states in different eras (Egypt, Persia), so pick the
// polity whose dates are nearest the snapshot; further than POLITY_SLACK years away it is not that state.
export const POLITY_SLACK = 30;

export function polityFor(p, year, polities = state.polities, byId = polityById) {
  let best = null, bestGap = Infinity;
  for (const name of [p.NAME, p.SUBJECTO]) {
    for (const id of (name && polities.names[name]) || []) {
      const polity = byId.get(id);
      const end = polity.end !== undefined ? polity.end : Infinity;
      const gap = year < polity.start ? polity.start - year : year > end ? year - end : 0;
      if (gap < bestGap) { best = polity; bestGap = gap; }
    }
    if (best && bestGap <= POLITY_SLACK) break; // the realm itself wins over its ruling power
  }
  return best && bestGap <= POLITY_SLACK ? best : null;
}

// Never rejects; polity cards just stay off if the file is missing.
export function loadPolities() {
  return getJson("data/polities.json")
    .then((data) => {
      state.polities = data;
      for (const polity of data.polities) polityById.set(polity.id, polity);
    })
    .catch((error) => console.warn("Could not load polities (" + error.message + ")"));
}
