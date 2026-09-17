#!/usr/bin/env python3
"""Append entries to a reference.json collection — validates, dedupes, writes.

Usage:
    python3 scripts/add_utterances.py <new-entries.json> [collection] [<db.json>]

<new-entries.json> is a JSON array (or single object) of candidate entries in
the reference schema documented in UTTERANCE_FETCH.md. `collection` defaults to
"utterances" (the other is "ran"); <db.json> defaults to reference.json in the
repo root.

Reference material is hand-curated and separate from vocab.json — it never
enters the review queue. This script keeps additions safe: it checks the schema,
confirms each `group` exists in the target collection, dedupes on `hanzi`, and
appends in place. Duplicates are skipped with a warning; schema errors abort
with nothing written. Draft new entries in a scratch file and run this rather
than hand-editing reference.json.
"""
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

# Every string field is required and non-empty. `group` is checked against the
# collection's own group ids; `sources` is an array, handled separately.
REQUIRED = [
    "hanzi", "pinyin", "gloss", "group", "note",
    "example", "example_pinyin", "example_translation",
]
SOURCE_LANGS = {"zh", "en"}


def fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def norm(s):
    return unicodedata.normalize("NFC", s.strip().lower())


def validate_sources(src, i):
    """`sources` is a non-empty array of {url, note, lang} objects.

    For an utterance the source is *usage evidence* — a real place the phrase is
    said this way (a clip, a comment thread, an online colloquial dictionary),
    not a fabricated origin story. url must be copied from a real result.
    """
    if not isinstance(src, list) or not src:
        return [f"entry {i}: 'sources' must be a non-empty array of {{url, note, lang}} objects"]
    errs = []
    for j, s in enumerate(src, 1):
        if not isinstance(s, dict):
            errs.append(f"entry {i} source {j}: must be an object with url/note/lang")
            continue
        url, note, lang = s.get("url"), s.get("note"), s.get("lang")
        if not isinstance(url, str) or not re.match(r"https?://\S", url.strip()):
            errs.append(f"entry {i} source {j}: 'url' must be an http(s) link")
        if not isinstance(note, str) or not note.strip():
            errs.append(f"entry {i} source {j}: 'note' must be a non-empty string")
        if lang not in SOURCE_LANGS:
            errs.append(f"entry {i} source {j}: 'lang' must be 'zh' or 'en'")
    return errs


def validate(entry, i, group_ids):
    errs = []
    for field in REQUIRED:
        v = entry.get(field)
        if not isinstance(v, str) or not v.strip():
            errs.append(f"entry {i}: missing or empty '{field}'")
    errs += validate_sources(entry.get("sources"), i)
    if errs:
        return errs
    if entry["group"] not in group_ids:
        errs.append(f"entry {i} ({entry['hanzi']}): group '{entry['group']}' "
                    f"not one of {sorted(group_ids)}")
    for f in ("pinyin", "example_pinyin"):
        if re.search(r"[a-zA-Zü]\d", entry[f]):
            errs.append(f"entry {i} ({entry['hanzi']}): '{f}' looks like tone numbers — "
                        f"use tone marks (ā á ǎ à)")
    # `blend` is optional — a note on how the characters slur together in fast
    # speech. If present it must be a non-empty string.
    b = entry.get("blend")
    if b is not None and (not isinstance(b, str) or not b.strip()):
        errs.append(f"entry {i} ({entry['hanzi']}): 'blend' must be a non-empty string if present")
    return errs


def main():
    if len(sys.argv) < 2:
        fail(__doc__.strip())
    new_path = Path(sys.argv[1])
    collection = sys.argv[2] if len(sys.argv) > 2 else "utterances"
    db_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).parent.parent / "reference.json"

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
    if collection not in db:
        fail(f"collection '{collection}' not in {db_path} (have: {', '.join(db)})")

    coll = db[collection]
    group_ids = {g["id"] for g in coll["groups"]}

    errs = [e for i, c in enumerate(candidates, 1) for e in validate(c, i, group_ids)]
    if errs:
        print("\n".join(errs))
        fail("schema validation failed — nothing written")

    seen = {norm(e["hanzi"]) for e in coll["items"]}
    added, skipped = [], []
    for c in candidates:
        if norm(c["hanzi"]) in seen:
            skipped.append(c["hanzi"])
            continue
        coll["items"].append(c)
        seen.add(norm(c["hanzi"]))
        added.append(c["hanzi"])

    if added:
        db_path.write_text(json.dumps(db, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")

    by_group = Counter(e["group"] for e in coll["items"])
    labels = {g["id"]: g["label"] for g in coll["groups"]}
    print(f"added {len(added)} to {collection}: {', '.join(added) or '—'}")
    if skipped:
        print(f"skipped duplicates: {', '.join(skipped)}")
    print(f"total {len(coll['items'])} | "
          + ", ".join(f"{labels.get(g, g)} {n}" for g, n in
                      sorted(by_group.items(), key=lambda kv: [x['id'] for x in coll['groups']].index(kv[0]))))


if __name__ == "__main__":
    main()
