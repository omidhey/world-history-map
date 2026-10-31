// State shared between the modules. Modules mutate this one object (an exported `let` cannot be
// reassigned from another module).

import { CATEGORIES } from "./categories.js";

export const state = {
  snapshots: [],        // border snapshots from data/borders/manifest.json
  requested: -1,        // index of the snapshot the slider asked for
  entries: [],
  currentList: [],      // entries in the requested period
  polities: { polities: [], names: {} },
  rulerData: {},
  areaData: {},
  openIds: null,        // ids of the card(s) shown, or null for the list
  openPolity: null,     // {id, props, year} when a state's card is shown instead
  followed: null,       // ISO code of the country being followed, or null
  followData: null,     // its lineage file
  followLayer: null,
  countryIndex: {},
  countryShapes: {},
};

export const polityById = new Map();
export const enabled = new Set(CATEGORIES.map(([key]) => key));
