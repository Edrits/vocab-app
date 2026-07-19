#!/usr/bin/env python3
"""Append new vocab entries to vocab.json — validates, dedupes, then writes.

Usage:
    python3 scripts/add_words.py <new-entries.json> [<db.json>]

<new-entries.json> is a JSON array (or single object) of candidate entries in
the schema documented in DAILY_FETCH.md. <db.json> defaults to vocab.json in
the repo root.

Agents: never hand-edit vocab.json or read it wholesale — draft your new
entries in a scratch file and run this. Duplicates are skipped with a warning;
schema errors abort with no changes written.
"""
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

REQUIRED = [
    "id", "hanzi", "pinyin", "literal", "meaning", "meaning_zh",
    "example", "example_pinyin", "example_translation", "context",
    "category", "date_added",
]
CATEGORIES = {"slang", "social", "meme", "abbreviation", "news", "chengyu"}


def fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def norm(s):
    return unicodedata.normalize("NFC", s.strip().lower())


def validate(entry, i):
    errs = []
    for field in REQUIRED:
        v = entry.get(field)
        if not isinstance(v, str) or not v.strip():
            errs.append(f"entry {i}: missing or empty '{field}'")
    if errs:
        return errs
    if entry["category"] not in CATEGORIES:
        errs.append(f"entry {i} ({entry['hanzi']}): category '{entry['category']}' "
                    f"not one of {sorted(CATEGORIES)}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", entry["date_added"]):
        errs.append(f"entry {i} ({entry['hanzi']}): date_added must be YYYY-MM-DD")
    for f in ("pinyin", "example_pinyin"):
        if re.search(r"[a-zA-Zü]\d", entry[f]):
            errs.append(f"entry {i} ({entry['hanzi']}): '{f}' looks like tone numbers — "
                        f"use tone marks (ā á ǎ à)")
    if not re.fullmatch(r"[a-z0-9-]+", entry["id"]):
        errs.append(f"entry {i} ({entry['hanzi']}): id must be kebab-case ascii")
    return errs


def main():
    if len(sys.argv) < 2:
        fail(__doc__.strip())
    new_path = Path(sys.argv[1])
    db_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent.parent / "vocab.json"

    try:
        candidates = json.loads(new_path.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"cannot parse {new_path}: {e}")
    if isinstance(candidates, dict):
        candidates = [candidates]
    if not isinstance(candidates, list) or not candidates:
        fail(f"{new_path} must be a JSON array of entries (or one object)")

    try:
        db = json.loads(db_path.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"cannot parse {db_path}: {e}")

    errs = [e for i, c in enumerate(candidates, 1) for e in validate(c, i)]
    if errs:
        print("\n".join(errs))
        fail("schema validation failed — nothing written")

    ids = {norm(e["id"]) for e in db}
    hanzi = {norm(e["hanzi"]) for e in db}
    added, skipped = [], []
    for c in candidates:
        if norm(c["id"]) in ids or norm(c["hanzi"]) in hanzi:
            skipped.append(c["hanzi"])
            continue
        db.append(c)
        ids.add(norm(c["id"]))
        hanzi.add(norm(c["hanzi"]))
        added.append(c["hanzi"])

    if added:
        db_path.write_text(json.dumps(db, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")

    cats = Counter(e["category"] for e in db)
    chengyu = cats.get("chengyu", 0)
    ratio = f"1 per {len(db) // chengyu}" if chengyu else "none yet"
    print(f"added {len(added)}: {', '.join(added) or '—'}")
    if skipped:
        print(f"skipped duplicates: {', '.join(skipped)}")
    print(f"total {len(db)} | chengyu {chengyu} ({ratio}) | "
          + ", ".join(f"{k} {v}" for k, v in sorted(cats.items())))


if __name__ == "__main__":
    main()
