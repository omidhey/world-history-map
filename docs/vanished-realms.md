# Vanished realms: why states disappear and come back on the map

Checked 2026-10-19 with `pipeline/gap_report.py` on the 14 snapshots in `data/borders/`.

Of 1,194 realm names, 49 are missing from at least one snapshot and then come back later. For each gap,
the script takes the realm's territory from the last snapshot that shows it and measures which polygons
cover that land in the gap year. Re-run it with:

```
.venv/Scripts/python pipeline/gap_report.py
```

Each gap has one of five causes. Section 6 describes the project rule that keeps land coloured.

## 1. The land really belonged to another state (correct)

These match the historical record. The realm was absorbed, partitioned or ruled by an empire, then restored.

| Realm                                                     | Gap year           | Who holds the land in the data                                                      |
| --------------------------------------------------------- | ------------------ | ----------------------------------------------------------------------------------- |
| Egypt                                                     | 500 BCE            | Achaemenid Empire                                                                   |
| Egypt                                                     | 323 BCE            | Empire of Alexander                                                                 |
| Egypt                                                     | 1 BCE / 400        | Roman / Eastern Roman Empire                                                        |
| Egypt                                                     | 800 / 1200 / 1500  | Abbasid / Fatimid Caliphate / Mamluk Sultanate                                      |
| Egypt                                                     | 1800               | Ottoman Empire                                                                      |
| Armenia                                                   | 400 / 800          | Persia / Abbasid Caliphate and Khazars                                              |
| Armenia                                                   | 1500 / 1800 / 1945 | White Sheep Turks / Ottomans and Persia / USSR                                      |
| Georgia, Azerbaijan                                       | 1800, 1945         | Russian Empire, USSR                                                                |
| Hungary, Croatia                                          | 1500–1914          | Kingdom of Hungary, Austrian Empire, Austria-Hungary; Croatia in Yugoslavia in 1945 |
| Poland                                                    | 1800 / 1914        | Prussia, Austria, Russia (the partitions, 1772–1795); restored 1918                 |
| Persia                                                    | 800 / 1200 / 1500  | Abbasid Caliphate / Buyid and Ghaznavid emirates / White Sheep Turks and Timurids   |
| Tibet                                                     | 1800               | Qing Empire                                                                         |
| Cyprus                                                    | 1800 / 1914 / 1945 | Ottoman Empire / United Kingdom                                                     |
| Burma, Cambodia, Laos, Cochin China                       | 1914               | British Raj, French Indochina                                                       |
| Mali, Senegal, Ghana (ancient)                            | 1914               | French West Africa                                                                  |
| Benin                                                     | 1914               | Nigeria (British)                                                                   |
| Madagascar, Martinique, Mozambique, Angola, Malawi, Libya | 1914 or 1945       | French, Portuguese, British and Italian colonial names                              |
| Japan                                                     | 1945               | "Japan (USA)", the US occupation                                                    |
| Serbia, Montenegro                                        | 1945               | Yugoslavia                                                                          |
| Hadramaut                                                 | 800                | Abbasid Caliphate                                                                   |

## 2. Same state, different name (correct, but looks like a change)

Upstream uses the period name, so the colour changes even though the country did not.

| Name | Gap year | Name used instead |
|---|---|---|
| Sweden, Denmark, Norway | 1500 | Kalmar Union |
| Norway | 1800 | Denmark-Norway |
| Japan | 1200 / 1914 | Imperial Japan (Fujiwara) / Empire of Japan |
| United Kingdom | 1914 | United Kingdom of Great Britain and Ireland |
| Champa | 1200 | Champa City States |
| Ethiopia | 1914 | Abyssinia |
| Oman | 1914 | British Protectorate |
| Beothuk | 1200 | "Boethuk" (spelling) |
| Aboriginal Tasmanians | 2000 BCE–1500 | Tasmanian hunter-gatherers |

A future aliases file (roadmap Session 15) can give these one identity and one colour.

## 3. Our own pipeline dropped land (fixed)

Two bugs in Session 2's simplification made realms vanish:

- Rounding coordinates (`-o precision=0.0001`) collapsed whole features: 149 in 1 BCE, 30 in 1500.
- `keep-shapes` protects only whole features, so islands inside a multi-part realm disappeared: Cyprus
  from the Ottoman Empire, Sicily and Sardinia from Rome, Canada's Arctic islands. That was 11–65
  islands larger than ~600 km² per snapshot.

`pipeline/download_borders.py` now drops the rounding, splits every realm into its parts before
simplifying and joins them again afterwards. No island larger than ~600 km² is lost in any snapshot.

## 4. Upstream gaps and mistakes (corrected by this project)

Where upstream left land unnamed or gave it to the wrong state, and the history is clear, we correct
it in [`data/borders/overrides.json`](../data/borders/overrides.json). The pipeline applies these after
simplifying. Corrected areas have a purple dashed outline on the map, and their tooltip explains the change.

| Year | Upstream shows | Corrected to | Source |
|---|---|---|---|
| 1800 | Taiwan unnamed | Taiwan Prefecture, Qing Empire (1684–1895) | [Taiwan under Qing rule](https://en.wikipedia.org/wiki/Taiwan_under_Qing_rule) |
| 1800 | "Sotho" in southern Nigeria | Kingdom of Benin (to 1897) | [Kingdom of Benin](https://en.wikipedia.org/wiki/Kingdom_of_Benin) |
| 1200 | Sri Lanka part of the Chola Empire | Kingdom of Polonnaruwa (Cholas expelled about 1070) | [Kingdom of Polonnaruwa](https://en.wikipedia.org/wiki/Kingdom_of_Polonnaruwa) |
| 400 | Arakan unnamed | Waithali kingdom (about 370–818) | [Waithali kingdom](https://en.wikipedia.org/wiki/Waithali_kingdom) |
| 800 | Arakan inside "Rajput Clans and Small States" | Waithali kingdom | same |
| 1500 | Nepal split between Tibet and the Delhi Sultanate | Malla kingdoms and hill principalities | [Malla dynasty](https://en.wikipedia.org/wiki/Malla_dynasty_(Nepal)), [Unification of Nepal](https://en.wikipedia.org/wiki/Unification_of_Nepal) |
| 323 BCE | Newfoundland unnamed | Paleo-Inuit, Groswater (from about 800 BCE) | [Groswater culture](https://en.wikipedia.org/wiki/Groswater_culture), [Heritage NL](https://www.heritage.nf.ca/articles/indigenous/palaeo-eskimo.php) |
| 1945 | Malta missing | Crown Colony of Malta (1813–1964) | [Crown Colony of Malta](https://en.wikipedia.org/wiki/Crown_Colony_of_Malta) |

Carved shapes reuse the realm's outline from the nearest snapshot that has it, so their borders are
approximate (`BORDERPRECISION` 1).

## 5. Left as is, for now

| Case | Why it is not corrected |
|---|---|
| Large unnamed areas (one covers most of Africa in 800, another West Africa to the Red Sea in 1500) | Upstream background land with no recorded polity. Naming it needs real research per region, not one label. |
| Mali in 1800 (43 % unnamed, rest Kaarta and Segu) | The Mali Empire had shrunk to the small Kangaba state; its old land was largely Bambara kingdoms, which is what the data shows. |
| Eastern North American hunter-gatherers (1 BCE, 400) | Partly replaced by named cultures (Hopewell and others); the rest is unnamed upstream. |
| Bhutan in 1500 | Bhutan was not unified until 1616, and upstream's 1200 outline for it also covers Assam, so there is no sound shape to carve. |
| Japan in 1200 called "Fujiwara" | A naming quibble (the Kamakura shogunate began in 1185), not a territorial error. |
| Bahamas, Turks and Caicos Islands in 1914 | Missing upstream (British colonies at the time); add them to `overrides.json` with a `copy` from 1800 once checked. |

## Adding a correction

Add an entry to `data/borders/overrides.json` with `id`, `year`, `op` (`rename`, `carve` or `copy`),
the new properties in `set`, a one-sentence `note` and at least one entry in `sources`. Then re-run
`pipeline/download_borders.py`. The script stops if an entry matches nothing, so a typo cannot fail silently.

## 6. Project rule: coloured land never goes back to uncoloured

Inhabited land that a realm held in one snapshot is never shown as uncoloured in a later one.
Where the source leaves land unnamed, `pipeline/carry_forward.py` gives it the realm recorded there
in the previous snapshot. This repeats from snapshot to snapshot, so it can reach back several snapshots.

Before the rule, 2,000–4,000 square degrees of once-coloured land (roughly the size of Europe to
twice that) lost its colour in each snapshot from 500 BCE to 1800. Now only slivers smaller than
~600 km² remain. Antarctica is left out because it has no permanent population.

Carried areas are shown **pale with a dotted outline**. Their tooltip reads "Last recorded here (year):
name", plus a note that the source records no realm there in the current year. They are not
presented as fact. A carried name can outlive the real realm, e.g. "N. European Bronze Age
cultures" in 400 CE or Dorset in 1800. The tooltip states the year it was last recorded, so the
reader can judge.

`gap_report.py` ignores carried areas, so it still measures what the source records.

