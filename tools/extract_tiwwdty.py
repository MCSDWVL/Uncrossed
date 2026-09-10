#!/usr/bin/env python3
"""Extract readable clue records from Matt Ginsberg's binary clue database.

The database stores a verified length-prefixed answer lexicon followed by a
custom clue-record section. Each clue record has text plus answer references.
The reference is an encoded answer ordinal: ``reference >> 1`` indexes the
length-prefixed lexicon; its low bit is retained as metadata.
"""
import argparse
import csv
import struct
from pathlib import Path

FIELDS = ["clue", "answer", "answer_resolution", "answer_refs", "answer_flags", "cluedata_offset", "source"]
INDICATORS = ("heard", "sounds like", "sound like", "reportedly", "report of", "we hear", "say", "spoken")

def read_words(data):
    count = struct.unpack_from("<I", data, 0)[0]
    words, position = [], 4
    for _ in range(count):
        length = data[position]
        word = data[position + 1:position + 1 + length]
        if not word or any(byte not in b"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" for byte in word):
            raise ValueError(f"Invalid answer lexicon record at byte {position}")
        text = word.decode("ascii")
        words.append(text)
        position += length + 1
    return words, position

def printable_clue(value):
    return (4 <= len(value) <= 250 and b" " in value and
            all(byte in (9, 10, 13) or 32 <= byte < 127 for byte in value))

def record_at(data, position, word_data_end):
    """Return (next_position, clue, refs) for a credible record, else None."""
    if position + 9 > len(data): return None
    length = data[position]
    end = position + 1 + length
    text = data[position + 1:end]
    if not printable_clue(text) or end + 4 > len(data): return None
    ref_count = struct.unpack_from("<I", data, end)[0]
    if not 1 <= ref_count <= 64 or end + 4 + 4 * ref_count > len(data): return None
    refs = struct.unpack_from(f"<{ref_count}I", data, end + 4)
    # References point into the answer/index area; this guards against false
    # positives found inside prose clue text.
    if any(ref >= word_data_end for ref in refs): return None
    return end + 4 + 4 * ref_count, text.decode("ascii"), refs

def iter_records(data, word_data_end):
    """Scan around custom index blocks and yield only structurally valid records."""
    position = word_data_end
    while position < len(data):
        parsed = record_at(data, position, word_data_end)
        if parsed is None:
            position += 1
            continue
        next_position, clue, refs = parsed
        yield position, clue, refs
        position = next_position

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("content/tiwwdty/cluedata"))
    parser.add_argument("--output", type=Path, default=Path("content/tiwwdty-extract.csv"))
    parser.add_argument("--max-records", type=int, default=500, help="Bounded output size; 0 means all")
    parser.add_argument("--homophones-only", action="store_true", help="Keep likely sound-alike clue wording")
    args = parser.parse_args()
    data = args.input.read_bytes()
    words, word_data_end = read_words(data)
    rows, unresolved = [], 0
    for offset, clue, refs in iter_records(data, word_data_end):
        if args.homophones_only and not any(marker in clue.lower() for marker in INDICATORS):
            continue
        ordinals = [ref >> 1 for ref in refs]
        if any(ordinal >= len(words) for ordinal in ordinals):
            answer, resolution = "", "unresolved-invalid-ordinal"
            unresolved += 1
        else:
            answer, resolution = " | ".join(words[ordinal] for ordinal in ordinals), "encoded-answer-ordinal"
        rows.append({"clue": clue, "answer": answer, "answer_resolution": resolution, "answer_refs": "|".join(map(str, refs)), "answer_flags": "|".join(str(ref & 1) for ref in refs), "cluedata_offset": offset, "source": "Matt Ginsberg's Crossword Clue Database (final edition, 2023)"})
        if args.max_records and len(rows) >= args.max_records: break
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
    print(f"Answer lexicon: {len(words):,} entries; clue records exported: {len(rows):,}; unresolved mappings: {unresolved:,}.")
    print(f"Wrote {args.output}. Decoded rows are ready for bounded candidate generation and review.")

if __name__ == "__main__": main()
