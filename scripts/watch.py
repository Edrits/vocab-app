#!/usr/bin/env python3
"""Manage watchlist.json — terms the daily fetch skipped but wants to revisit.

Usage:
    python3 scripts/watch.py list
    python3 scripts/watch.py add <candidates.json>
    python3 scripts/watch.py drop <hanzi> [<reason>]

`list` prints every watched term with its status, and first removes any term
that has since made it into vocab.json ("graduated"). Statuses:
    due      — backfill items (always), or first seen 28+ days ago: decide now,
               add it to the deck if it is still in use, otherwise drop it
    stale    — not sighted for 42+ days: it has probably died, drop it
    watching — too early to judge, leave it

`add` takes a JSON array (or single object) of {hanzi, reason, note}. A term
already on the list gets its sighting count and last_seen bumped and the note
appended; a term already in the deck is skipped. `reason` is one of:
    too-new     trending, but too fresh to know whether it will last
    unverified  meaning/origin couldn't be confirmed against a source
    niche       stuck in one community, person or fandom so far
    backfill    an established term the deck is missing — add when there's room

Agents: never hand-edit watchlist.json — use this script.
"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WATCH = ROOT / "watchlist.json"
VOCAB = ROOT / "vocab.json"
REASONS = {"too-new", "unverified", "niche", "backfill"}
DUE_AFTER = 28    # days since first seen before a decision is due
STALE_AFTER = 42  # days since last sighting before it counts as dead


def fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def load():
    return json.loads(WATCH.read_text(encoding="utf-8")) if WATCH.exists() else []


def save(items):
    WATCH.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def deck_hanzi():
    return {e["hanzi"] for e in json.loads(VOCAB.read_text(encoding="utf-8"))}


def age(d):
    return (date.today() - date.fromisoformat(d)).days


def status(item):
    if age(item["last_seen"]) >= STALE_AFTER:
        return "stale"
    if item["reason"] == "backfill" or age(item["first_seen"]) >= DUE_AFTER:
        return "due"
    return "watching"


def cmd_list():
    items = load()
    deck = deck_hanzi()
    graduated = [i["hanzi"] for i in items if i["hanzi"] in deck]
    if graduated:
        items = [i for i in items if i["hanzi"] not in deck]
        save(items)
        print("graduated (now in deck, removed):", " ".join(graduated))
    if not items:
        print("watchlist empty")
        return
    order = {"due": 0, "stale": 1, "watching": 2}
    for i in sorted(items, key=lambda i: (order[status(i)], i["first_seen"])):
        print(f"[{status(i)}] {i['hanzi']} · {i['reason']} · seen {i['sightings']}x, "
              f"first {i['first_seen']}, last {i['last_seen']} — {i['note']}")


def cmd_add(path):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    cands = raw if isinstance(raw, list) else [raw]
    items = load()
    by_hanzi = {i["hanzi"]: i for i in items}
    deck = deck_hanzi()
    today = date.today().isoformat()
    for n, c in enumerate(cands):
        for k in ("hanzi", "reason", "note"):
            if not isinstance(c.get(k), str) or not c[k].strip():
                fail(f"candidate {n}: missing or empty '{k}'")
        if c["reason"] not in REASONS:
            fail(f"candidate {n}: reason must be one of {sorted(REASONS)}")
    for c in cands:
        h = c["hanzi"].strip()
        if h in deck:
            print(f"skip {h}: already in the deck")
        elif h in by_hanzi:
            i = by_hanzi[h]
            if i["last_seen"] != today:
                i["sightings"] += 1
                i["last_seen"] = today
            i["reason"] = c["reason"]
            i["note"] = f"{i['note']} | {today}: {c['note']}"
            print(f"bumped {h} (seen {i['sightings']}x)")
        else:
            items.append({"hanzi": h, "reason": c["reason"], "first_seen": today,
                          "last_seen": today, "sightings": 1, "note": c["note"]})
            print(f"added {h}")
    save(items)
    print(f"watchlist: {len(items)} terms")


def cmd_drop(hanzi, reason=""):
    items = load()
    kept = [i for i in items if i["hanzi"] != hanzi]
    if len(kept) == len(items):
        fail(f"{hanzi} is not on the watchlist")
    save(kept)
    print(f"dropped {hanzi}" + (f" ({reason})" if reason else "") + f" — watchlist: {len(kept)} terms")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["list"]:
        cmd_list()
    elif args[:1] == ["add"] and len(args) == 2:
        cmd_add(args[1])
    elif args[:1] == ["drop"] and len(args) in (2, 3):
        cmd_drop(*args[1:])
    else:
        print(__doc__)
        sys.exit(1)
