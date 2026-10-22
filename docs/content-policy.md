# Content policy

This is how every addition and correction is judged. It is short on purpose. When in doubt,
open an issue and ask.

## 1. No source, no merge

Every record and every correction needs at least one source a reviewer can check.

- **Good sources:** Wikidata items, encyclopedia articles (Wikipedia, Britannica,
  Encyclopaedia Iranica, Stanford Encyclopedia of Philosophy…), academic books and papers,
  museum and university pages. Give a link, or author + title + page for print.
- **Not enough on its own:** blogs, forums, social media, AI-generated text, "everyone knows".
- Wikipedia is fine as a starting source. For disputed or surprising claims, also cite what
  the Wikipedia article itself cites.

## 2. Write in your own words

Summaries are one or two sentences, written by you. Do not paste text from Wikipedia, books
or other websites, even with a link: link to them instead. Text you write is published under
CC BY-SA 4.0 ([LICENSE-TEXT.md](../LICENSE-TEXT.md)).

## 3. Neutral wording

Describe, don't judge. Prefer "ruled X from 1501 to 1524" over "the great ruler who
restored X's glory". Use the names that scholarly sources use for the period, and mention
other common names where it helps ("Byzantine Empire (Eastern Roman Empire)").

## 4. Dates

- Years are integers; **negative means BCE; there is no year 0** (1 BCE is followed by 1 CE).
- Say how precise a date is (`date_precision`). Uncertain ancient dates are normal: mark
  them `circa`, `decade` or `century` rather than inventing exactness.

## 5. Disputed facts are shown as disputed

When good sources disagree (a birth year, a reign, who held a border), do not pick a winner.
Set `disputed: true` and add each version as a separate claim with its own source
(see [schema.md](schema.md)). The map shows both.

## 6. Borders

Borders come from [historical-basemaps](https://github.com/aourednik/historical-basemaps)
and are approximate. Report a border error with a source; corrections are made as sourced
entries in `data/borders/overrides.json`, outlined in purple on the map
([vanished-realms.md](vanished-realms.md)). Where possible we also send the fix upstream.

## 7. What gets rejected

- Unsourced claims, or sources that do not say what the record says.
- Copied text (see section 2).
- Political advocacy: wording or edits meant to support a present-day territorial,
  national or religious claim. History of contested places is welcome when it is sourced
  and neutral.
- Original research: your own theory, however good, needs a published source first.
- Spam, advertising, vandalism, and anything that breaks the
  [Code of Conduct](../CODE_OF_CONDUCT.md).

A rejected suggestion gets a short reason. You are welcome to fix it and try again.
