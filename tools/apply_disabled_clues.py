#!/usr/bin/env python3
"""Apply disabled clue IDs to an already-built static catalog.

Use this when only content/disabled-clues.json changed. A full build is still
required after changing source data or any compiler filtering rules.
"""
import argparse
import gzip
import json
from pathlib import Path


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    temporary.replace(path)


def disabled_entries(path):
    if not path.exists():
        return set()
    data = load(path)
    return set(data.get("disabled", data))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=Path("dist"))
    parser.add_argument("--disabled", type=Path, default=Path("content/disabled-clues.json"))
    args = parser.parse_args()
    root, disabled = args.directory, disabled_entries(args.disabled)
    index_path = root / "data" / "answers-index.json"
    index = load(index_path)
    removed = 0

    down_counts = {}
    for letter in "abcdefghijklmnopqrstuvwxyz":
        path = root / "data" / "down" / f"{letter}.json"
        data = load(path)
        original = data["clues"]
        data["clues"] = [clue for clue in original if clue["id"] not in disabled]
        removed += len(original) - len(data["clues"])
        down_counts[letter.upper()] = len(data["clues"])
        if len(data["clues"]) != len(original):
            write(path, data)

    surviving_answers = set()
    across_clues = 0
    for path in (root / "data" / "across").glob("*.json"):
        data = load(path)
        answers = {
            word: [clue for clue in clues if clue["id"] not in disabled]
            for word, clues in data["answers"].items()
        }
        removed += sum(len(data["answers"][word]) - len(clues) for word, clues in answers.items())
        data["answers"] = {word: clues for word, clues in answers.items() if clues}
        surviving_answers.update(data["answers"])
        across_clues += sum(map(len, data["answers"].values()))
        if data["answers"] != load(path)["answers"]:
            write(path, data)

    index["answers"] = [entry for entry in index["answers"] if entry["word"] in surviving_answers]
    index["downCounts"] = down_counts
    write(index_path, index)

    manifest_path = root / "data" / "manifest.json"
    manifest = load(manifest_path)
    files = [path for path in root.rglob("*") if path.is_file() and path.name != "manifest.json"]
    sizes = {str(path.relative_to(root)).replace("\\", "/"): path.stat().st_size for path in files}
    gzip_sizes = {name: len(gzip.compress((root / name).read_bytes(), mtime=0)) for name in sizes}
    manifest.update({
        "answers": len(index["answers"]),
        "acrossClues": across_clues,
        "downClues": sum(down_counts.values()),
        "totalBytes": sum(sizes.values()),
        "totalGzipBytes": sum(gzip_sizes.values()),
        "files": sizes,
        "gzipFiles": gzip_sizes,
    })
    write(manifest_path, manifest)
    print(f"Applied {len(disabled):,} disabled IDs; removed {removed:,} published clues.")


if __name__ == "__main__":
    main()
