#!/usr/bin/env python3
"""Draft review-only clue candidates with the OpenAI Responses API.

The output is deliberately untrusted editorial material. No row is approved,
and no row is published until it passes tools/compile_catalog.py after review.
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

FIELDS = ["id", "letter", "clue_text", "mechanism", "surface_answer", "pronunciation_variant", "frequency", "source_type", "source_reference", "source_fact", "draft_method", "status", "editor_notes", "duplicate_key", "topic"]
LETTER_SURFACES = {
    "A": ["a", "aye"], "B": ["bee", "be"], "C": ["sea", "see"], "D": ["dee"], "E": ["eye"], "F": ["eff"], "G": ["gee"], "H": ["aitch"], "I": ["eye"], "J": ["jay"], "K": ["kay"], "L": ["ell"], "M": ["em"], "N": ["en"], "O": ["owe"], "P": ["pea"], "Q": ["queue", "cue"], "R": ["are"], "S": ["ess"], "T": ["tea", "tee"], "U": ["you", "ewe"], "V": ["vee"], "W": ["double-u"], "X": ["ex"], "Y": ["why"], "Z": ["zee", "zed"]
}

def request_candidates(api_key, model, letter, count):
    prompt = f'''Draft exactly {count} distinct candidate clues for a browser word game. Every clue's answer must be exactly the single capital letter {letter}. The player sees the clue alone, so it must be fair for a general US English audience.

Allowed mechanisms: homophone, direct-letter-fact, abbreviation-or-symbol, reference-or-trivia, wordplay. Broad playful wordplay is welcome, but do not rely on a niche fact, current event, regional-only pronunciation, or a clue with multiple plausible letter answers. Likely spoken surfaces for {letter}: {', '.join(LETTER_SURFACES[letter])}.

Return JSON only: an array of objects with keys clue_text, mechanism, surface_answer, source_fact, and research_hint. surface_answer must be the non-letter word being clued (for example bee), or an empty string for direct letter facts. source_fact should be a short factual claim to verify, not copied source prose. Never say that these clues are approved. Do not include the answer letter itself in clue_text.'''
    body = json.dumps({"model": model, "input": [{"role": "developer", "content": "You draft entertaining but rigorously fair word-game clue candidates. Return only valid JSON."}, {"role": "user", "content": prompt}]}).encode("utf-8")
    request = urllib.request.Request("https://api.openai.com/v1/responses", data=body, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=90) as response:
        payload = json.load(response)
    texts = [part.get("text", "") for item in payload.get("output", []) for part in item.get("content", []) if part.get("type") == "output_text"]
    if not texts: raise ValueError("Responses API returned no output_text.")
    text = "\n".join(texts).strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
    parsed = json.loads(text)
    if not isinstance(parsed, list): raise ValueError("Expected a JSON array.")
    return parsed

def safe_rows(items, letter, model):
    rows, seen = [], set()
    for item in items:
        clue = str(item.get("clue_text", "")).strip()
        mechanism = str(item.get("mechanism", "")).strip()
        surface = str(item.get("surface_answer", "")).strip().lower()
        key = re.sub(r"[^a-z0-9]+", "", clue.lower())
        if not clue or key in seen:
            continue
        seen.add(key)
        rows.append({"id": f"llm-{letter}-{len(rows)+1:03}", "letter": letter, "clue_text": clue, "mechanism": mechanism, "surface_answer": surface, "pronunciation_variant": "", "frequency": "", "source_type": "LLM candidate — research required", "source_reference": str(item.get("research_hint", "")).strip(), "source_fact": str(item.get("source_fact", "")).strip(), "draft_method": f"OpenAI Responses API ({model})", "status": "candidate", "editor_notes": "Verify fact/pronunciation and edit for fairness before approval.", "duplicate_key": key, "topic": ""})
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("content/candidates.csv"))
    parser.add_argument("--letters", default="ABCDEFGHIJKLMNOPQRSTUVWXYZ", help="Letters to draft, e.g. ABC")
    parser.add_argument("--count", type=int, default=40, help="Requested candidates per letter")
    parser.add_argument("--model", default="gpt-5-mini")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--append", action="store_true", help="Append rows instead of replacing the CSV")
    args = parser.parse_args()
    letters = "".join(dict.fromkeys(args.letters.upper()))
    if not letters or any(letter not in LETTER_SURFACES for letter in letters): parser.error("--letters must contain A–Z only")
    if args.count < 1 or args.count > 100: parser.error("--count must be 1–100")
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"Set {args.api_key_env} before drafting; no API call was made.")
    rows = []
    for letter in letters:
        for attempt in range(3):
            try:
                rows.extend(safe_rows(request_candidates(api_key, args.model, letter, args.count), letter, args.model)); break
            except (urllib.error.HTTPError, urllib.error.URLError, ValueError, json.JSONDecodeError) as error:
                if attempt == 2: raise SystemExit(f"{letter} failed after 3 attempts: {error}")
                time.sleep(2 ** attempt)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if args.append and args.output.exists() else "w"
    with args.output.open(mode, encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS)
        if mode == "w": writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} review-only candidates to {args.output}. None are approved.")

if __name__ == "__main__": main()
