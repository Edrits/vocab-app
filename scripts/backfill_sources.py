#!/usr/bin/env python3
"""Patch `sources` onto existing vocab.json entries, in place.

Usage:
    python3 scripts/backfill_sources.py <patch.json> [<db.json>]

<patch.json> is a JSON array of objects, each { "id": <existing-id>,
"sources": [<citation string>, ...] }. Every id must already exist in the
deck and every sources array must hold one or more non-empty strings.
Unknown ids or bad shapes abort with nothing written.

This is the ONLY sanctioned way to hand-modify vocab.json — it touches only
the `sources` field of the named entries and preserves everything else and
the file's formatting. New entries still go through add_words.py.
"""
import json
import sys
from pathlib import Path

# Reuse the exact same source-shape validation as new entries.
sys.path.insert(0, str(Path(__file__).parent))
from add_words import validate_sources


def fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        fail(__doc__.strip())
    patch_path = Path(sys.argv[1])
    db_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent.parent / "vocab.json"

    try:
        patches = json.loads(patch_path.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"cannot parse {patch_path}: {e}")
    if isinstance(patches, dict):
        patches = [patches]
    if not isinstance(patches, list) or not patches:
        fail(f"{patch_path} must be a JSON array of {{id, sources}} objects")

    try:
        db = json.loads(db_path.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"cannot parse {db_path}: {e}")
    by_id = {e["id"]: e for e in db}

    errs, seen = [], set()
    for i, p in enumerate(patches, 1):
        pid = p.get("id")
        src = p.get("sources")
        if not isinstance(pid, str) or pid not in by_id:
            errs.append(f"patch {i}: id {pid!r} not found in deck")
            continue
        if pid in seen:
            errs.append(f"patch {i}: duplicate id {pid!r} in patch file")
        seen.add(pid)
        errs += validate_sources(src, i)
    if errs:
        print("\n".join(errs))
        fail("validation failed — nothing written")

    for p in patches:
        by_id[p["id"]]["sources"] = p["sources"]

    db_path.write_text(json.dumps(db, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    remaining = sum(1 for e in db if not e.get("sources"))
    print(f"patched {len(patches)} entr{'y' if len(patches)==1 else 'ies'}: "
          + ", ".join(p["id"] for p in patches))
    print(f"total {len(db)} | still missing sources: {remaining}")


if __name__ == "__main__":
    main()
