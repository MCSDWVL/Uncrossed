# Uncrossed

A dependency-free daily word game. The checked-in `dist/` directory is the deployable site; raw clue databases stay local and are never uploaded.

## Build the deployable site

Obtain the local Lexicon JSONL and (optionally) CMUdict, then run this one-liner from the project root. It reads the local Ginsberg database, emits a compact answer index plus lazy letter and across-clue shards, and copies the site shell into `dist/`.

```powershell
python tools/build_static_assets.py --words T:/OtherProjects/Lexicon/word-candidates-definition-and-frequency.jsonl
```

If you later download CMUdict, add `--cmudict path/to/cmudict.dict` to broaden phonetic matching.

Then verify and serve the result:

```powershell
python tools/verify_static_assets.py; python -m http.server 8000 --directory dist
```

Open `http://localhost:8000`. Add `?seed=2026-09-10` to reproduce a specific Pacific-date puzzle. Commit `dist/` and push `main`; the included Pages workflow deploys that prebuilt directory. The workflow does not run the compiler.

To suppress a bad clue without revising source data, add its generated ID (for example `g-12345-678`) to `content/disabled-clues.json` and rebuild.

## Development fallback

Without generated data, serve this directory with any static-file server; it uses the small starter catalog. For example:

```powershell
python -m http.server 8000
```

## Checks

```powershell
node tools/test_game.mjs
python -m py_compile tools/build_static_assets.py tools/verify_static_assets.py
```

## Content

The deployable corpus is built offline and includes source, session, conventional, and starter down clues by default. See [content/README.md](content/README.md) for source and removal details.
