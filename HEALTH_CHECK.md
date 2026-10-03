# Health check prompt

Paste (or say "run HEALTH_CHECK.md") to get a bounded bug sweep of the app.

---

Do a **read-only health check** of this app. Goal: a short, ranked list of real bugs — not a code-style review, not a refactor plan. Don't edit anything until I approve the list.

**Scope, in priority order** (stop going deeper once you hit diminishing returns):
1. `index.html` JS — read it fully, once. Focus on: SRS `grade()`/`nextStep()`/`repairState()` maths (NaN, undefined fields, dates/timezones, interval regressions); due-queue building; streak/打卡 and "today" logic across midnight and timezones; localStorage parse/upgrade paths (missing/corrupt blobs, entries whose `id` no longer exists); sync (pull/push races, last-write-wins on `meta.lastSaved`, clobbering local progress with an older/empty remote, PIN handling, offline errors); quiz distractor generation with small categories; reference modes lazy-load; HTML injection from data fields rendered via `innerHTML`.
2. `sync-worker/worker.js` — CORS, method/size checks, missing-PIN handling, error responses.
3. `scripts/*.py` — validation gaps that would let a bad entry into the JSON.
4. Data integrity — **via scripts, never by reading `vocab.json`/`reference.json` wholesale**: one Python one-liner checking duplicate `id`/`hanzi`, missing required fields, malformed `sources`, unknown categories, pinyin with tone numbers, reference items whose `group` isn't declared.
5. Runtime smoke test — serve on :4173, load in the browser pane, click through Study / Quiz / Browse / Me / ☰ reference modes, check the console for errors. Also try one fresh-state load (empty localStorage). Don't touch the real sync PIN or push anything to the Worker.

**Rules to stay sane:**
- Each finding needs a concrete trigger ("if X then Y breaks") and a `file:line`. If you can't name a trigger, drop it or mark it "speculative".
- Cosmetic issues, naming, "could be refactored", missing tests: leave them out, or at most one line under "nits".
- Don't chase the same theory for more than a couple of steps. Note it and move on.
- No commits, no pushes, no Worker deploys.

**Output:** a table ranked by severity (🔴 loses/corrupts progress · 🟠 visibly wrong behaviour · 🟡 edge case), with columns: what, trigger, location, suggested fix (one line). Then a "checked and fine" line so I know what was covered. Keep the whole thing under ~40 lines.
