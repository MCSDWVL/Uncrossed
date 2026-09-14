#!/usr/bin/env python3
"""Build the publishable, lazy-loaded Uncrossed data set locally.

The raw crossword database and Lexicon input are deliberately inputs only.
Nothing in them is copied verbatim to the site other than selected clue text.
Run this before deploying the contents of dist/ to GitHub Pages.
"""
import argparse
import gzip
import hashlib
import json
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from extract_tiwwdty import iter_records, read_words
from build_candidates import LETTER_PHONES, phones

SOURCE = "Crossword clues sourced from Matt Ginsberg's Crossword Clue Database (final edition, 2023)"
ALPHA = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
# The surface word is the configuration boundary for pronunciation judgment.
# Values in ``near`` are intentionally labelled in the puzzle UI. For example,
# HAY is accepted for A, but players are told it is only nearly a homophone.
HOMOPHONE_SURFACES = {
    "A": {"exact": {"EH", "EY", "AY"}, "near": {"HAY", "HEY"}},
    "B": {"exact": {"BEE", "BE"}}, "C": {"exact": {"SEA", "SEE"}},
    "D": {"exact": {"DEE"}}, "E": {"exact": {"EE", "EEE"}, "near": {"HE"}}, "F": {"exact": {"EFF"}}, "G": {"exact": {"GEE"}},
    "H": {"exact": {"AITCH"}}, "I": {"exact": {"EYE", "AYE"}}, "J": {"exact": {"JAY"}}, "K": {"exact": {"KAY"}},
    "L": {"exact": {"ELL"}}, "M": {"exact": {"EM"}, "near": {"THEM"}}, "N": {"exact": {"EN", "IN"}, "near": {"END"}}, "O": {"exact": {"OH", "OWE"}},
    "P": {"exact": {"PEA", "PEE"}}, "Q": {"exact": {"QUEUE", "CUE"}}, "R": {"exact": {"ARE"}},
    "S": {"exact": {"ESS", "ES"}}, "T": {"exact": {"TEA", "TEE"}}, "U": {"exact": {"YOU", "EWE", "YEW", "EU"}},
    "V": {"exact": {"VEE"}}, "W": {"exact": {"DOUBLEU"}}, "X": {"exact": {"EX"}}, "Y": {"exact": {"WHY"}}, "Z": {"exact": {"ZEE"}},
}
# EEE is a legitimate spoken surface for E, but the source corpus heavily
# concentrates it in footwear-width clues. Keep those clues available without
# allowing them to crowd out the rest of the E catalog.
SHOE_SIZE_CLUE = re.compile(
    r"\b(?:shoe|shoes|shoebox|boot|boots|bootery|sneaker|sneakers|foot|feet|footwear|"
    r"bigfoot|brannock|brogan|brogue|clodhopper|florsheim|hush\s+pupp(?:y|ies)|loafer|loafers|"
    r"moccasin|moccasins|oxford|oxfords|pump|pumps|sandal|sandals|slipper|slippers|sole|soles|"
    r"timberland|thom\s+mcans?|zappos|toe|toes|wide|width|wedge|wedgie|size|sizes|fitting|"
    r"fit|last|kicks|footprint)\b",
    re.IGNORECASE,
)

def source_topic(letter, answer, clue):
    if letter == "E" and answer == "EEE" and SHOE_SIZE_CLUE.search(clue):
        return "shoe-size"
    return None

def homophone_kind(letter, answer, pronunciations):
    """Return ``exact`` or ``near`` when this surface can clue a letter."""
    surfaces = HOMOPHONE_SURFACES[letter]
    for kind, words in surfaces.items():
        if answer in words:
            return kind
    if pronunciations and pronunciations.get(answer, set()) & {tuple(LETTER_PHONES[letter])}:
        return "exact"
    return None

def compact(value):
    return re.sub(r"\s+", " ", value).strip()

def identifier(prefix, *parts):
    value = "|".join(str(part) for part in parts).encode("utf-8")
    return f"{prefix}-{hashlib.sha1(value).hexdigest()[:16]}"

def hygienic(clue, answer):
    clue = compact(clue)
    if not (4 <= len(clue) <= 250) or not clue.isprintable():
        return False
    # Do not publish clues which visibly give away their answer, or mostly enumerate it.
    normalized = re.sub(r"[^A-Z]", "", clue.upper())
    if answer in normalized or re.fullmatch(r".*\(\s*\d+\s*\).*", clue):
        return False
    return True

def word_frequencies(path):
    result = {}
    with path.open(encoding="utf-8") as source:
        for line in source:
            try:
                item = json.loads(line)
                word = str(item.get("word", "")).upper()
                zipf = float(item.get("zipf", 0) or 0)
            except (ValueError, json.JSONDecodeError):
                continue
            if word.isalpha() and zipf >= 4:
                result[word] = max(zipf, result.get(word, 0))
    return result

def disabled_entries(path):
    if not path.exists(): return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return set(data.get("disabled", data))

def starter_clues(repo):
    """Ask Node for the existing human-authored fallback catalog."""
    script = "import {CLUES} from './js/runtime-data.js'; console.log(JSON.stringify(CLUES));"
    output = subprocess.check_output(["node", "--input-type=module", "-e", script], cwd=repo, text=True)
    return json.loads(output)

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("content/tiwwdty/cluedata"))
    parser.add_argument("--words", type=Path, required=True, help="Lexicon JSONL containing word and zipf fields")
    parser.add_argument("--cmudict", type=Path, help="Optional CMUdict; improves letter-name homophone matching")
    parser.add_argument("--output", type=Path, default=Path("dist"))
    parser.add_argument("--disabled", type=Path, default=Path("content/disabled-clues.json"))
    args = parser.parse_args()
    repo = Path(__file__).resolve().parent.parent
    frequencies, disabled = word_frequencies(args.words), disabled_entries(args.disabled)
    pronunciations = defaultdict(set)
    if args.cmudict:
        for pronunciation, values in phones(args.cmudict).items():
            for word in values: pronunciations[word.upper()].add(pronunciation)

    raw = args.input.read_bytes()
    answers, clue_start = read_words(raw)
    across, down, seen_across, seen_down = defaultdict(list), defaultdict(list), defaultdict(set), defaultdict(set)
    eligible = set()
    for offset, clue, refs in iter_records(raw, clue_start):
        clue = compact(clue)
        for reference in refs:
            answer = answers[reference >> 1]
            source_id = f"g-{offset}-{reference}"
            if source_id in disabled:
                continue
            if answer in frequencies and 6 <= len(answer) <= 10 and hygienic(clue, answer):
                key = clue.casefold()
                if key not in seen_across[answer]:
                    across[answer].append({"id": source_id, "clue": clue})
                    seen_across[answer].add(key)
                    eligible.add(answer)
            for letter in HOMOPHONE_SURFACES:
                kind = homophone_kind(letter, answer, pronunciations)
                if kind and hygienic(clue, answer):
                    key = clue.casefold()
                    if key not in seen_down[letter]:
                        item = {"id": source_id, "clue": clue, "mechanism": "source-homophone", "sourceAnswer": answer}
                        if kind == "near": item["homophone"] = "near"
                        topic = source_topic(letter, answer, clue)
                        if topic: item["topic"] = topic
                        down[letter].append(item)
                        seen_down[letter].add(key)

    # Existing authored, session, and conventional entries are approved by default.
    for letter, items in starter_clues(repo).items():
        for item in items:
            if item["id"] not in disabled and item["clue"].casefold() not in seen_down[letter]:
                down[letter].append({"id": item["id"], "clue": item["clue"], "mechanism": "starter"})
                seen_down[letter].add(item["clue"].casefold())
    with (repo / "content/session-candidates.csv").open(encoding="utf-8", newline="") as source:
        import csv
        for row in csv.DictReader(source):
            letter, clue = row.get("letter", ""), compact(row.get("clue_text", ""))
            if letter in ALPHA and clue and row.get("id") not in disabled and clue.casefold() not in seen_down[letter]:
                item = {"id": row["id"], "clue": clue, "mechanism": row.get("mechanism") or "session"}
                if row.get("mechanism") == "near-homophone": item["homophone"] = "near"
                if row.get("topic"): item["topic"] = row["topic"]
                down[letter].append(item)
                seen_down[letter].add(clue.casefold())
    for item in json.loads((repo / "content/conventional-facts.json").read_text(encoding="utf-8")):
        letter, clue = item["letter"], compact(item["fact"])
        if clue.casefold() not in seen_down[letter]:
            down[letter].append({"id": identifier("fact", letter, clue), "clue": clue, "mechanism": "conventional"})
            seen_down[letter].add(clue.casefold())

    # W is conventionally “double U.” Reuse the richer U catalog rather than
    # relying on the very small set of standalone W-name homophones.
    for item in down["U"]:
        clue = f"2× {item['clue']}"
        if clue.casefold() not in seen_down["W"]:
            copied = {"id": f"double-u-{item['id']}", "clue": clue, "mechanism": "double-u"}
            if item.get("sourceAnswer"): copied["sourceAnswer"] = item["sourceAnswer"]
            if item.get("homophone"): copied["homophone"] = item["homophone"]
            down["W"].append(copied)
            seen_down["W"].add(clue.casefold())

    destination = args.output.resolve()
    if destination.exists(): shutil.rmtree(destination)
    destination.mkdir(parents=True)
    for relative in ("index.html", "styles.css"):
        shutil.copy2(repo / relative, destination / relative)
    shutil.copytree(repo / "js", destination / "js")
    data_dir = destination / "data"
    for prefix in sorted({word[:2].lower() for word in eligible}):
        grouped = {word.lower(): across[word] for word in sorted(eligible) if word[:2].lower() == prefix}
        write_json(data_dir / "across" / f"{prefix}.json", {"v": 1, "answers": grouped})
    index = [{"word": word.lower(), "shard": word[:2].lower()} for word in sorted(eligible)]
    down_counts = {letter: len(down[letter]) for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
    write_json(data_dir / "answers-index.json", {"v": 1, "answers": index, "downCounts": down_counts})
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        write_json(data_dir / "down" / f"{letter.lower()}.json", {"v": 1, "letter": letter, "clues": down[letter]})
    files = [path for path in destination.rglob("*") if path.is_file() and path.name != "manifest.json"]
    sizes = {str(path.relative_to(destination)).replace("\\", "/"): path.stat().st_size for path in files}
    gzip_sizes = {name: len(gzip.compress((destination / name).read_bytes(), mtime=0)) for name in sizes}
    write_json(data_dir / "manifest.json", {"v": 1, "source": SOURCE, "answers": len(index), "acrossClues": sum(map(len, across.values())), "downClues": sum(map(len, down.values())), "totalBytes": sum(sizes.values()), "totalGzipBytes": sum(gzip_sizes.values()), "files": sizes, "gzipFiles": gzip_sizes})
    print(f"Built {destination}: {len(index):,} eligible answers, {sum(map(len, across.values())):,} across clues, {sum(map(len, down.values())):,} down clues.")

if __name__ == "__main__": main()
