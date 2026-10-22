# Record format

Every person, work, invention, ruler, dynasty or culture is one JSON file in
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
| `category` | yes | One of `philosopher`, `scientist`, `writer`, `work`, `invention`, `ruler`, `dynasty`, `culture`. |
| `start` | yes | Integer year, see "Years" below. People: birth. Dynasties and cultures: beginning. Works: composition or first version. Inventions: first known date. |
| `end` | no | Integer year. People: death. Dynasties and cultures: end. Works: completion, if composed over years. Leave out when there is none. |
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

## Checking your file

```
pip install -r pipeline/requirements.txt
python pipeline/validate.py
```

It prints one line per problem (`data/entries/x.json: start: there is no year 0 …`) and
fails if there are any. The same check runs automatically on every pull request.
