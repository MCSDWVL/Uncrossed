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
    for entry in index["answers"]:
        word, shard = entry["word"], entry["shard"]
        assert word.isalpha() and 6 <= len(word) <= 10 and shard == word[:2]
        clues = load(root / "data/across" / f"{shard}.json")["answers"].get(word)
        assert clues, f"No across clue for {word}."
    print(f"Verified {len(index['answers']):,} answers and generated data integrity in {root}.")

if __name__ == "__main__": main()
