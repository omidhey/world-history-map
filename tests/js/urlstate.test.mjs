// Run with:  node --test tests/js
import test from "node:test";
import assert from "node:assert/strict";

import { encodeState, decodeState, snapshotIndexFor } from "../../site/js/urlstate.js";
import { snapshotFor } from "../../site/js/categories.js";

const KEYS = ["philosopher", "writer", "event"];
const snaps = [-3000, -500, -323, -1, 400, 1500].map((year) => ({ year }));

test("round trip keeps BCE years and layers", () => {
  const search = encodeState({ year: -500, country: "IRN", layers: ["philosopher"], entry: "socrates" });
  assert.equal(search, "?year=-500&country=IRN&layers=philosopher&entry=socrates");
  assert.deepEqual(decodeState(search, KEYS), { year: -500, country: "IRN", layers: ["philosopher"], entry: "socrates" });
});

test("empty state gives an empty query; all layers on is omitted", () => {
  assert.equal(encodeState({ year: null, layers: null }), "");
  assert.equal(encodeState({ year: 1500, layers: null }), "?year=1500");
});

test("garbage is ignored", () => {
  assert.deepEqual(decodeState("?year=abc&country=<x>&layers=bogus&entry=a/b", KEYS), {});
  assert.deepEqual(decodeState("?year=0", KEYS), {}); // there is no year 0
  assert.deepEqual(decodeState("?layers=writer,bogus,writer", KEYS), { layers: ["writer"] });
});

test("an entry wins over a polity; polity alone is kept", () => {
  assert.equal(decodeState("?entry=x&polity=y", KEYS).polity, undefined);
  assert.equal(decodeState("?polity=achaemenid-empire", KEYS).polity, "achaemenid-empire");
});

test("snapshotIndexFor takes the latest snapshot at or before the year", () => {
  assert.equal(snapshotIndexFor(snaps, -500), 1);
  assert.equal(snapshotIndexFor(snaps, -400), 1);
  assert.equal(snapshotIndexFor(snaps, -4000), 0);
  assert.equal(snapshotIndexFor(snaps, 2020), 5);
  assert.equal(snapshotIndexFor([], 5), -1);
});

test("snapshotFor keeps the current snapshot when the entry is in view, else the nearest overlapping one", () => {
  const socrates = { start: -470, end: -399 };           // period -500..-324 is index 1
  assert.equal(snapshotFor(socrates, snaps, 1), 1);
  assert.equal(snapshotFor(socrates, snaps, 5), 1);
  const long = { start: -600, end: 100 };                // overlaps indexes 1..3
  assert.equal(snapshotFor(long, snaps, 5), 3);
  assert.equal(snapshotFor(long, snaps, 2), 2);
  assert.equal(snapshotFor({ start: -9000, end: -8000 }, snaps, 3), 0); // before the first snapshot
});
