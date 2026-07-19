# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal, single-user web app for learning trending Chinese *netizen* vocabulary (internet slang, memes, social trends, the odd chengyu) with spaced-repetition flashcards. No build step, no framework — plain static files, plus one tiny Cloudflare Worker for progress sync.

## Running it

```
./start.command          # opens the app in the browser + serves on :4173
# or:
python3 -m http.server 4173   # then visit http://localhost:4173
```

The app **must** be served over HTTP, not opened as a `file://` — it `fetch`es `vocab.json`, which browsers block on the file protocol.

There are no tests, linter, or build. Verify changes by loading the page and exercising the tabs.

## Deployment

Live at **https://edrits.github.io/vocab-app/** via GitHub Pages, serving the `main` branch of `github.com/Edrits/vocab-app` (root folder). Deploying = pushing to `main`; Pages picks it up within a couple of minutes. Edward uses it from his phone as a home-screen web app, so after a vocab fetch or app change, commit and push to make it reach him.

## Architecture

Four moving parts:

- **`vocab.json`** — the entire database: a flat array of word entries. Each entry's schema and the quality bar are documented in `DAILY_FETCH.md`. **Don't read it wholesale or hand-edit it — it grows daily.** To see what's in the deck, extract keys via a shell one-liner (see `DAILY_FETCH.md`); to add words, write the new entries to a scratch file and run `python3 scripts/add_words.py <file>`, which validates, dedupes on `id`/`hanzi`, appends, and prints deck stats.
- **`index.html`** — the whole app (markup, CSS, and vanilla JS inline). Four tabs: **Study** (SM-2-lite flashcards), **Quiz** (multiple-choice rounds, XP only — never touches the SRS schedule), **Browse** (search/sort/filter list), and **Me** (netizen rank + XP, 打卡 streak heatmap, word of the day, mastery). Pinyin renders tone-coloured via `tonePinyin()`; audio uses the browser's built-in zh-CN speech synthesis. Category styling keys off `cat-<category>` classes (e.g. chengyu renders gold).
- **`DAILY_FETCH.md`** — the recipe an agent follows to research trending terms and append them to `vocab.json`. A scheduled task (`daily-netizen-vocab-fetch`, ~06:30 daily, runs while the Claude app is open on this Mac) executes it automatically; "grab today's words" runs it on demand. Keep roughly one chengyu per ~10 words, and commit + push afterwards so the live site updates.
- **`sync-worker/worker.js`** — a Cloudflare Worker (deployed at `vocab-sync.neddritchie.workers.dev`, KV namespace bound as `SYNC`) that stores one progress blob per PIN (keyed by SHA-256 of the `X-Pin` header). The client half lives in `index.html` (`SYNC_URL` constant): pull on open/foreground, debounced push after every save, last-write-wins on `meta.lastSaved`. **The repo copy of worker.js is the source of truth, but deploys are manual** — Edward pastes it into the Cloudflare dashboard (no wrangler/Node on this Mac), so flag loudly if you change it.

Key design point: **review progress lives in the browser's `localStorage`** (SRS state under `netizen-vocab-srs-v1`; XP/streak/activity under `netizen-vocab-meta-v1`; sync PIN under `netizen-vocab-sync-pin`), never in `vocab.json`. Cloud sync mirrors those blobs to the Worker but the same rule holds: don't write SRS state into `vocab.json`.

## Conventions

- Use **UK spelling** in any user-facing copy and comments (e.g. *colour*, *practise*, *behaviour*).
- Pinyin uses tone marks (ā á ǎ à), not tone numbers.
