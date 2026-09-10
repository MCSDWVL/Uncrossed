#!/usr/bin/env python3
"""Create spreadsheet candidates from the local word/definition/Zipf JSONL.

This is deliberately a discovery aid. It does not approve or publish clues.
For homophone discovery, download CMUdict separately and pass --cmudict.
"""
import argparse
import csv
import json
import re
from pathlib import Path

LETTER_PHONES = {
    "A": ("EY",), "B": ("B", "IY"), "C": ("S", "IY"), "D": ("D", "IY"),
    "E": ("IY",), "F": ("EH", "F"), "G": ("JH", "IY"), "H": ("EY", "CH"),
    "I": ("AY",), "J": ("JH", "EY"), "K": ("K", "EY"), "L": ("EH", "L"),
    "M": ("EH", "M"), "N": ("EH", "N"), "O": ("OW",), "P": ("P", "IY"),
    "Q": ("K", "Y", "UW"), "R": ("AA", "R"), "S": ("EH", "S"), "T": ("T", "IY"),
    "U": ("Y", "UW"), "V": ("V", "IY"), "W": ("D", "AH", "B", "AH", "L", "Y", "UW"),
    "X": ("EH", "K", "S"), "Y": ("W", "AY"), "Z": ("Z", "IY"),
}
FIELDS = ["id", "letter", "clue_text", "mechanism", "surface_answer", "pronunciation_variant", "frequency", "source_type", "source_reference", "source_fact", "draft_method", "status", "editor_notes", "duplicate_key"]

def phones(path: Path):
    result = {}
    with path.open(encoding="latin-1") as source:
        for line in source:
            line = line.strip()
            if not line or line.startswith(";;;"):
                continue
            word, *pronunciation = line.split()
            word = re.sub(r"\(\d+\)$", "", word).lower()
            pronunciation = tuple(re.sub(r"\d", "", phone) for phone in pronunciation)
            result.setdefault(pronunciation, set()).add(word)
    return result

def common_words(path: Path):
    result = {}
    with path.open(encoding="utf-8") as source:
        for line in source:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            word = str(item.get("word", "")).lower()
            if word.isalpha() and float(item.get("zipf", 0) or 0) >= 3.5:
                result[word] = item
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--words", type=Path, required=True, help="word-candidates-definition-and-frequency.jsonl")
    parser.add_argument("--cmudict", type=Path, required=True, help="Downloaded CMUdict cmudict.dict")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    words, pronunciation_index = common_words(args.words), phones(args.cmudict)
    rows = []
    for letter, phonemes in LETTER_PHONES.items():
        for word in sorted(pronunciation_index.get(phonemes, set())):
            item = words.get(word)
            if not item or word == letter.lower():
                continue
            definition = str(item.get("definition", "")).strip()
            rows.append({"id": f"candidate-{letter}-{word}", "letter": letter, "clue_text": "", "mechanism": "homophone", "surface_answer": word, "pronunciation_variant": "CMUdict", "frequency": item.get("zipf", ""), "source_type": "CMUdict + Wiktextract", "source_reference": word, "source_fact": definition, "draft_method": "source-discovery", "status": "candidate", "editor_notes": "Write original clue wording; verify fairness.", "duplicate_key": ""})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
    print(f"Wrote {len(rows)} unapproved candidates to {args.output}")

if __name__ == "__main__": main()
