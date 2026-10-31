// Run with:  node --test tests/js
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import { buildIndex, search } from "../../site/js/searchindex.js";

const entries = [
  { id: "socrates", name: "Socrates", location: { place: "Athens" }, summary: "Athenian philosopher.", category: "philosopher" },
  { id: "aristotle", name: "Aristotle", location: { place: "Athens" }, summary: "Pupil of Plato, teacher of Alexander.", category: "philosopher" },
  { id: "plato", name: "Plato", location: { place: "Athens" }, summary: "Founded the Academy; student of Socrates.", category: "philosopher" },
];
const polities = [{ id: "achaemenid-empire", name: "Achaemenid Empire", capital: { place: "Persepolis" }, summary: "Persian empire." }];
const index = buildIndex(entries, polities);

test("exact and misspelled names find the entry first", () => {
  assert.equal(search(index, "Socrates")[0].id, "socrates");
  assert.equal(search(index, "Aristotel")[0].id, "aristotle");
  assert.equal(search(index, "sokrates")[0].id, "socrates");
});

test("states are found and marked as polities", () => {
  const hit = search(index, "achaemenid")[0];
  assert.equal(hit.kind, "polity");
  assert.equal(hit.id, "achaemenid-empire");
});

test("places match; short queries and nonsense give nothing", () => {
  assert.equal(search(index, "Athens").length, 3);
  assert.deepEqual(search(index, "a"), []);
  assert.deepEqual(search(index, "zzzzqx"), []);
});

test("the real data set: well-known names rank first", () => {
  let real;
  try { real = JSON.parse(readFileSync(new URL("../../site/data/entries.json", import.meta.url), "utf8")); } catch { return; } // site/data is generated
  const big = buildIndex(real, []);
  const t = performance.now();
  for (const [query, id] of [["Socrates", "socrates"], ["Confucius", "confucius"]]) {
    assert.equal(search(big, query)[0].id, id, query);
  }
  assert.ok(performance.now() - t < 2000);
});
