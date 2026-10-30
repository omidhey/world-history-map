// Run with:  node --test tests/js
import test from "node:test";
import assert from "node:assert/strict";

import { formatYear, formatDates, colourFor, escapeHtml, suggestEditUrl } from "../../site/js/util.js";
import { periodOf, inPeriod } from "../../site/js/categories.js";

test("formatYear: negative is BCE, no year 0", () => {
  assert.equal(formatYear(-399), "399 BCE");
  assert.equal(formatYear(-1), "1 BCE");
  assert.equal(formatYear(1), "1 CE");
});

test("formatDates marks approximate and disputed dates", () => {
  assert.equal(formatDates({ start: -470, end: -399, date_precision: "year" }), "470 BCE – 399 BCE");
  assert.equal(formatDates({ start: -500, date_precision: "century", disputed: true }), "c. 500 BCE (disputed)");
});

test("colourFor is stable and distinguishes powers", () => {
  assert.equal(colourFor("Roman Empire"), colourFor("Roman Empire"));
  assert.notEqual(colourFor("Roman Empire"), colourFor("Han Empire"));
});

test("escapeHtml escapes markup", () => {
  assert.equal(escapeHtml('<a href="x">&</a>'), "&lt;a href=&quot;x&quot;&gt;&amp;&lt;/a&gt;");
});

test("suggestEditUrl pre-fills the issue form", () => {
  const url = new URL(suggestEditUrl("correct-entry.yml", "[Correction] x", { entry: "x" }));
  assert.equal(url.searchParams.get("template"), "correct-entry.yml");
  assert.equal(url.searchParams.get("entry"), "x");
});

test("periodOf: up to the year before the next snapshot, never year 0", () => {
  const snaps = [{ year: -1000 }, { year: 1 }, { year: 400 }];
  assert.deepEqual(periodOf(snaps, 0), { from: -1000, to: -1 });
  assert.deepEqual(periodOf(snaps, 1), { from: 1, to: 399 });
  assert.deepEqual(periodOf(snaps, 2, 2026), { from: 400, to: 2026 });
});

test("inPeriod uses the span of disputed records", () => {
  const period = { from: -1000, to: -1 };
  assert.ok(inPeriod({ start: -1100, end: -900 }, period));
  assert.ok(!inPeriod({ start: 5 }, period));
  assert.ok(inPeriod({ start: 5, span: [-1611, 5] }, period));
});
