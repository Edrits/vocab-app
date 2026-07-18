# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal, single-user web app for learning trending Chinese *netizen* vocabulary (internet slang, memes, social trends, the odd chengyu) with spaced-repetition flashcards. No build step, no framework, no backend — plain static files served locally.

## Running it

```
./start.command          # opens the app in the browser + serves on :4173
# or:
python3 -m http.server 4173   # then visit http://localhost:4173
```

The app **must** be served over HTTP, not opened as a `file://` — it `fetch`es `vocab.json`, which browsers block on the file protocol.

There are no tests, linter, or build. Verify changes by loading the page and exercising both modes.

## Architecture

Three moving parts:

- **`vocab.json`** — the entire database: a flat array of word entries. Each entry's schema and the quality bar are documented in `DAILY_FETCH.md`; follow it when adding words. Entries are keyed by a unique `id`; dedupe on `id`/`hanzi`.
- **`index.html`** — the whole app (markup, CSS, and vanilla JS inline). Two modes toggled by the header tabs: **Study** (SM-2-lite flashcards) and **Browse** (the sorter/filter list). Category styling keys off `cat-<category>` classes (e.g. chengyu renders gold).
- **`DAILY_FETCH.md`** — the recipe an agent follows to research trending terms and append them to `vocab.json`. The "grab today's words" workflow runs this. Keep roughly one chengyu per ~10 new words.

Key design point: **review progress lives in the browser's `localStorage`** (key `netizen-vocab-srs-v1`), never in `vocab.json`. This keeps the database clean and shareable, but means progress is per-device and resets if site data is cleared. Preserve this separation — don't write SRS state into `vocab.json`.

## Conventions

- Use **UK spelling** in any user-facing copy and comments (e.g. *colour*, *practise*, *behaviour*).
- Pinyin uses tone marks (ā á ǎ à), not tone numbers.
