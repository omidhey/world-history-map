# Contributing

Thank you for helping. This map grows through additions and corrections from anyone, and
every change is reviewed by an admin before it goes live.

Before you start, please read the one-page [content policy](docs/content-policy.md). The
short version: **no source, no merge**, write in your own words, stay neutral.

## Ways to help

| You want to… | Do this | Coding needed? |
|---|---|---|
| Add a person, work, invention, ruler… | Open an issue and describe it, with a source | No |
| Correct an entry | Open an issue saying what is wrong, with a source | No |
| Report a border error | Open an issue with the year, the place and a source | No |
| Add or fix records yourself | Edit or add a JSON file in `data/entries/` and open a pull request | A little |
| Improve the site or the pipeline | Open an issue first for anything larger than a small fix | Yes |

## Adding a record with a pull request

1. Fork the repository and create a branch.
2. Add one file per record in `data/entries/`, named after its `id`
   (for example `data/entries/socrates.json`). The format is described in
   [docs/schema.md](docs/schema.md).
3. Conventions:
   - Years are integers. **Negative means BCE. There is no year 0.**
   - Every record has at least one source in `sources`.
   - The `summary` is one or two sentences in your own words.
   - Disputed facts are marked as disputed, not decided (see the content policy).
4. Run the check locally (optional; it also runs automatically on your pull request):

   ```
   pip install -r pipeline/requirements.txt
   python pipeline/validate.py
   ```

5. Open a pull request. A pull request with a failing check cannot be merged.

## Running the site locally

See [README.md](README.md#run-it-locally-windows).

## How review works

Every issue and pull request is reviewed by the admin. You may be asked for a better source
or a rewording; that is normal and not a rejection.

## License of your contribution

By submitting an issue or pull request with content for this project, you agree that your
contribution is licensed under the project's terms: code and border data under
GPL-3.0-or-later ([LICENSE](LICENSE)), text under CC BY-SA 4.0
([LICENSE-TEXT.md](LICENSE-TEXT.md)).

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Report problems to
semifact@gmail.com.
