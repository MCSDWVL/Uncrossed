#!/usr/bin/env python3
"""Validate generated assets before they are committed or deployed."""
import argparse
import json
from pathlib import Path

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=Path("dist"))
    args = parser.parse_args()
    root = args.directory
    index = load(root / "data/answers-index.json")
    assert index.get("v") == 1
    assert len(index["answers"]) > 90, "Need more than 90 supported answers."
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        down = load(root / "data/down" / f"{letter.lower()}.json")
        assert down.get("letter") == letter and down.get("clues"), f"No down clues for {letter}."
        assert all(clue.get("homophone") in (None, "near") for clue in down["clues"]), f"Invalid homophone label for {letter}."
        assert all(not clue.get("topic") or clue["topic"] in ("fact", "letterplay", "shoe-size") for clue in down["clues"]), f"Invalid clue topic for {letter}."
    a_clues = load(root / "data/down/a.json")["clues"]
    assert all(clue.get("homophone") == "near" for clue in a_clues if clue.get("sourceAnswer") == "HAY"), "HAY clues for A must be marked as near homophones."
    e_clues = load(root / "data/down/e.json")["clues"]
    assert sum(clue.get("topic") == "shoe-size" for clue in e_clues) > 0, "E needs classified shoe-size clues."
    assert sum(clue.get("topic") in ("fact", "letterplay") for clue in e_clues) >= 20, "E needs the expanded authored clue pool."
    for entry in index["answers"]:
        word, shard = entry["word"], entry["shard"]
        assert word.isalpha() and 6 <= len(word) <= 10 and shard == word[:2]
        clues = load(root / "data/across" / f"{shard}.json")["answers"].get(word)
        assert clues, f"No across clue for {word}."
    print(f"Verified {len(index['answers']):,} answers and generated data integrity in {root}.")

if __name__ == "__main__": main()
