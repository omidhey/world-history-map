# Record format

Every person, work, invention, ruler, dynasty, culture or environmental event is one JSON file in
`data/entries/`, named after its `id` (`data/entries/socrates.json`). The machine-readable
version of this page is [pipeline/entry.schema.json](../pipeline/entry.schema.json);
[pipeline/validate.py](../pipeline/validate.py) checks it on every pull request.

## Example

```json
{
  "id": "socrates",
  "wikidata": "Q913",
  "name": "Socrates",
  "category": "philosopher",
  "start": -470,
  "end": -399,
  "date_precision": "year",
  "location": { "lat": 37.97, "lon": 23.72, "place": "Athens" },
  "summary": "Athenian thinker who wrote nothing himself and questioned his fellow citizens about justice and virtue; he was tried and sentenced to death by the city in 399 BCE.",
  "links": { "wikipedia": "https://en.wikipedia.org/wiki/Socrates" },
  "sources": ["https://www.wikidata.org/wiki/Q913", "https://en.wikipedia.org/wiki/Socrates"],
  "disputed": false
}
```

## Fields

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Stable identifier: lowercase words joined by hyphens (`cyrus-the-great`). Equals the file name. Never change it once merged. |
| `wikidata` | no | Wikidata item, e.g. `Q913`. Each item may appear in only one record. |
| `name` | yes | Common English name. |
| `category` | yes | One of `philosopher`, `scientist`, `writer`, `work`, `invention`, `ruler`, `dynasty`, `culture`, `event` (environmental event: eruption, climate episode, drought). |
| `start` | yes | Integer year, see "Years" below. People: birth. Dynasties and cultures: beginning. Works: composition or first version. Inventions: first known date. Events: onset. |
| `end` | no | Integer year. People: death. Dynasties and cultures: end. Works: completion, if composed over years. Events: end of the episode. Leave out when there is none (one-off eruptions). |
| `date_precision` | yes | How exact the dates are: `day`, `year`, `circa` (within a few years), `decade`, `century`. |
| `location` | yes | `lat`, `lon` (decimal degrees) and `place` (a name). The place most associated with the subject: where a person worked, a capital, where a work was written or an invention first made. |
| `summary` | yes | One or two sentences (20–400 characters) **in your own words**. Licensed CC BY-SA 4.0. |
| `links` | no | Further reading, e.g. `{"wikipedia": "https://…"}`. |
| `sources` | yes | At least one: a link, or author + title + page for print. **No source, no merge.** |
| `disputed` | no | `true` when good sources disagree. Requires `claims`. Default `false`. |
| `claims` | with `disputed` | Two or more competing values, each `{"field": "start" or "end", "value": year, "note": "…", "sources": [...]}`. |

No other fields are allowed; propose new ones in an issue.

## Years

- Years are integers. **Negative means BCE. There is no year 0**: 1 BCE (`-1`) is followed
  directly by 1 CE (`1`).
- Socrates was born in 470 BCE and died in 399 BCE: `"start": -470, "end": -399`.
- Some tools and datasets use a year 0 (astronomical numbering), which shifts every BCE
  date by one. Check a known date before importing.
- The Wikidata query service is one of them: it returns Socrates' birth as `-0469`, and it
  also converts Julian dates to Gregorian. `pipeline/import_wikidata.py` therefore reads dates
  from the entity data itself, which keeps the year as entered (`-0470`).
- `start` may not be after `end`, and no year may be in the future.

## Disputed dates

When sources disagree, keep the most commonly cited value in `start`/`end`, set
`disputed: true`, and list each version as a claim with its own source. From
`data/entries/gautama-buddha.json`:

```json
"start": -563,
"end": -483,
"date_precision": "circa",
"disputed": true,
"claims": [
  { "field": "start", "value": -563, "note": "Traditional chronology (563–483 BCE).", "sources": ["https://en.wikipedia.org/wiki/The_Buddha"] },
  { "field": "start", "value": -480, "note": "Many historians now prefer a later chronology (about 480–400 BCE).", "sources": ["https://en.wikipedia.org/wiki/The_Buddha"] }
]
```

## Polities

A state, empire or kingdom is one JSON file in `data/polities/`
([pipeline/polity.schema.json](../pipeline/polity.schema.json)). It links the names the border
snapshots use to a description, so clicking a realm on the map opens its card.

```json
{
  "id": "achaemenid-empire",
  "wikidata": "Q389688",
  "name": "Achaemenid Empire",
  "border_names": ["Achaemenid Empire"],
  "type": "empire",
  "start": -550,
  "end": -330,
  "date_precision": "year",
  "capital": { "lat": 29.93, "lon": 52.89, "place": "Persepolis" },
  "summary": "First Persian empire, founded by Cyrus the Great …",
  "links": { "wikipedia": "https://en.wikipedia.org/wiki/Achaemenid_Empire" },
  "sources": ["https://www.wikidata.org/wiki/Q389688", "https://en.wikipedia.org/wiki/Achaemenid_Empire"],
  "disputed": false
}
```

Same rules as entries for `id`, `wikidata`, `start`, `end`, `date_precision`, `summary`, `links`,
`sources`, `disputed` and `claims`. Different fields:

| Field | Required | Meaning |
|---|---|---|
| `border_names` | yes | Exact `NAME` values from `data/borders/*.geojson` that this state covers. The validator fails on a name that is in no snapshot. |
| `type` | yes | `empire`, `kingdom`, `republic`, `city-state`, `caliphate`, `sultanate`, `khanate`, `confederation`, `state` or `other`. |
| `capital` | no | `lat`, `lon`, `place`. |

The same border name may belong to different states in different eras (`Egypt`, `Persia`). Give each
state its own file with its own dates; the validator fails if two states claim a name at overlapping
dates. On the map a snapshot gets the card whose dates are nearest the snapshot's year, and none if
that is more than 30 years away. The ruling power (`SUBJECTO`) is tried when the realm itself has no card.

`pipeline/make_polities.py` writes the first batch from `pipeline/polities_seed.json` (it looks up
the Wikidata item from the Wikipedia title and never overwrites an existing file). After that,
edit the JSON files directly.

## Checking your file

```
pip install -r pipeline/requirements.txt
python pipeline/validate.py
```

It prints one line per problem (`data/entries/x.json: start: there is no year 0 …`) and
fails if there are any. The same check runs automatically on every pull request.

## Dynasties and rulers

A ruling house is one file in `data/dynasties/`, a ruler one file in `data/rulers/`
([dynasty.schema.json](../pipeline/dynasty.schema.json), [ruler.schema.json](../pipeline/ruler.schema.json)).
Both name the state they belong to in `polity` (an `id` from `data/polities/`) and follow the
same year, `date_precision`, `disputed`/`claims` and `sources` rules as other records.

- Dynasty: `start`/`end` are the years the house ruled **this state**.
- Ruler: `title` (king, emperor, caliph, pharaoh…), optional `dynasty` (a dynasty `id` of the same state), and `start`/`end` are the **reign**, not birth and death. Co-reigns may overlap.
- `validate.py` checks that the polity and dynasty exist and that dates lie within the state's dates give or take 30 years.

The lists are a selection, not every ruler. `pipeline/rulers_seed.py` holds the curated rows and
`pipeline/make_rulers.py` writes the files (adds Wikidata ids and Wikipedia sources, and prints reigns
that contradict Wikidata's birth or death years). Wikidata's own reign data is too thin for ancient
states to import directly (checked in Session 16), so rows are written by hand from Wikipedia.
