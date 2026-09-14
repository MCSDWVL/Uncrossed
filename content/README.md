# Content workflow

## Published-corpus workflow

The current release workflow is deliberately permissive: Ginsberg across clues and identified letter-name homophone clues ship after mechanical hygiene filtering. The original session candidates, conventional facts, and starter clues also ship by default. Editorial review is optional; remove a bad generated ID through `disabled-clues.json` and rebuild.

The build excludes generic down clues such as “Alphabet letter,” “Letter of the alphabet,” and “Alphabetic character,” which do not identify a particular letter. Specific clues such as “Eighth letter” remain eligible.

`tools/build_static_assets.py` is an offline-only compiler. It reads `tiwwdty/cluedata`, a local Lexicon JSONL (Zipf >= 4), and optionally CMUdict; it writes only derived browser assets under `dist/`. The browser loads the answer index and down catalog first, then one two-letter across shard for the day. Do not commit the raw input files.

The game bundle uses `js/runtime-data.js`. It intentionally contains a small, hand-reviewed starter catalog (five clues per letter), so the site can run immediately. Before public launch, grow this to the planned 20 approved clues per letter using the workflow below.

## Sources

1. The local Wiktextract export is the source for English definitions, tags, and IPA evidence. Read it as a streaming JSONL file; never copy its gloss prose into the shipped clue.
2. CMU Pronouncing Dictionary is the canonical ARPAbet source for identifying letter-name homophones. Keep its license notice in the offline content directory when downloaded.
3. WordNet 3.1 corroborates semantic candidates and flags overly broad definitions.
4. Wikidata supplies stable trivia facts. Store a QID plus the property/value used in the candidate record; write fresh clue text.
5. `conventional-facts.json` is the hand-maintained source for Roman numerals, chemical symbols, grades, and other tightly scoped conventions.

## Review CSV

The required columns are `id,letter,clue_text,mechanism,surface_answer,pronunciation_variant,frequency,source_type,source_reference,source_fact,draft_method,status,editor_notes,duplicate_key`; an optional `topic` classifies a clue for selection diversity. Use `near-homophone` as the mechanism when a session clue is deliberately a close pronunciation rather than an exact letter-name match; it is displayed to players as “nearly a homophone.” Source surfaces are configured in `HOMOPHONE_SURFACES` in `tools/build_static_assets.py` with the same distinction (for example, `HAY` for `A`).

Only `approved` rows compile. An editor must reject clues with a second plausible letter answer, unverified facts, regional-only pronunciation assumptions, specialist knowledge, answer-revealing wording, or duplicated wording.

## Fast batch drafting

For a large review batch, set `OPENAI_API_KEY` and run:

```powershell
python tools/draft_clues.py --count 40 --output content/candidates.csv
```

This calls the Responses API once per letter and creates review-only rows. It does not approve or publish anything. Review candidates in the CSV, mark good rows `approved`, then compile directly into the live module:

```powershell
python tools/compile_catalog.py --input content/candidates.csv --minimum 20
```

The compiler defaults to `js/generated-clues.js`, which the game imports automatically. If the 20-per-letter gate fails, the existing starter catalog remains in use.

Run `python tools/build_candidates.py --help` to produce a phonetic starter CSV from a local word file and CMUdict.

## Ginsberg clue database

`tools/extract_tiwwdty.py` extracts a bounded, traceable CSV from the local final-edition database:

```powershell
python tools/extract_tiwwdty.py --max-records 500 --output content/tiwwdty-extract.csv
python tools/extract_tiwwdty.py --homophones-only --max-records 250 --output content/tiwwdty-homophones.csv
```

The database stores its answer references as encoded lexicon ordinals. The extractor decodes them and retains the raw reference and flag, so output can be used to create bounded across and homophone candidate sets. Every selected clue still requires editorial review.
