# Daily netizen-vocab fetch — agent recipe

This is the task the scheduled agent runs each morning to grow `vocab.json`.

## Goal
Add up to 3–5 Chinese netizen terms that are **genuinely useful and likely to last** — words a
learner will still meet in a year — and append them to `vocab.json`, never duplicating a term
already in the file. Favour the **durable core** over the merely fresh: it is fine to add fewer,
or to backfill an enduring term the deck has somehow missed, rather than reach for something
fleeting to hit a number. **Does this belong? (the endurance bar)** below is now the main filter —
apply it to everything before it goes in.

## Token discipline (important — the database grows daily)
Never read `vocab.json` into context and never hand-edit it. It gains ~4 entries a day;
reading it wholesale will eventually cost hundreds of thousands of tokens per run.
You only ever need the *keys*, via the commands below.

## Steps
1. **List what exists** (instead of reading the file). Run:
   ```
   python3 -c "import json; d=json.load(open('vocab.json')); print(len(d), 'words:', ' '.join(e['hanzi'] for e in d))"
   ```
   This gives you the full dedupe list for a few tokens per word. The chengyu ratio and
   category counts are printed by the append script in step 5, or on demand:
   ```
   python3 -c "import json, collections; print(collections.Counter(e['category'] for e in json.load(open('vocab.json'))))"
   ```
2. **Search** for candidates. Rotate across sources so results stay varied:
   - Weibo hot search (微博热搜), Douyin / RedNote (小红书) trending, Bilibili
   - 年度网络流行语 / word-of-the-year lists (国家语言资源监测与研究中心, 《咬文嚼字》, 小红书年度热词) —
     these are already filtered for endurance, so they're a better hunting ground than raw hot-search
   - **established terms that are everywhere but the deck simply hasn't got yet** — backfilling the
     durable core is as valuable as catching something new
   - only then, this week's genuinely-spreading new terms — and hold them to the endurance bar below
3. **Select** terms that are (a) not already in the deck, (b) genuinely in use — not textbook
   words, (c) explainable with real cultural context, and (d) **likely to endure** (see the bar
   below). Prefer a mix of categories, and lead with the solid, established core.
   - **Chengyu rule:** include roughly **one classic chengyu (成语) per ~10 new words added**.
     Prefer chengyu that still circulate in online/comment culture, and in the `context`
     field note how netizens actually use it. Use category `chengyu`. Don't force one into
     every batch — track the running ratio (about 1 in 10).
   - **Vocab vs. meme — be honest about which.** Not everything trending is a reusable piece
     of vocabulary with a stable, portable meaning. Some things are really a one-off meme,
     joke, or news reference that people are talking about right now (e.g. "PPT永动机" isn't
     an expression with a fixed sense — it's a riff on a specific joke/story). Don't force
     these into a dictionary-style "netizens use this to mean X" definition; that manufactures
     a meaning that isn't really there. Instead, go find out the actual facts/event/post behind
     it and write `meaning`/`context` as reporting: what's actually happening, why it's funny
     or resonant, where it originated. Use category `meme` for these rather than `slang`.
     **But raise the bar for memes now:** only add one that has genuinely **spread and stuck**
     (across platforms, over weeks — not days). A one-off joke confined to one community, or this
     week's format, is a reference, not vocabulary — skip it (see the endurance bar).
4. For each term, **verify meaning/usage** against at least one source before writing it —
   do not invent definitions. For meme entries specifically, dig up the real originating
   event/post/screenshot rather than guessing at a generic "meaning" — the fact pattern is
   the whole point. If unsure about a term, drop it rather than guess.
   **Record the source(s) you used in the entry's `sources` array** (URLs or short citations,
   Mandarin or English) — this is required, not optional.
5. **Append via the script** — write your new entries (ALL fields below) as a JSON array
   to a scratch file *outside the repo* (e.g. `$TMPDIR/new_words.json`), then run:
   ```
   python3 scripts/add_words.py "$TMPDIR/new_words.json"
   ```
   It validates the schema, skips anything already in the deck, appends the rest, and
   prints the new totals including the chengyu ratio. If it reports schema errors, fix
   your scratch file and re-run — never edit `vocab.json` directly.
6. Commit `vocab.json` with a message like `vocab: add N terms (YYYY-MM-DD)` and push
   (push = deploy via GitHub Pages).

## Does this belong? (the endurance bar)
The deck is meant to be **solid vocabulary**, not a museum of dead memes. The hard part is telling
real 网络用语 — a word people keep reaching for — from a passing reference (a streamer's slip, one
game forum's in-joke) that will be gone in a month. Weigh these before adding anything:

**Signs it will LAST — add it:**
- **Fills a real gap** — names a feeling, situation or social type people keep needing to describe
  (内卷, 躺平, 情绪价值, 松弛感, 班味). A concept, not a punchline.
- **Used productively** — people apply it to new situations and combine it, not just quote the original.
- **Crossed over** — seen well beyond its origin community; ideally picked up by mainstream media or a
  year-end 流行语 list.
- **Already has some age** — surviving a few months is the best predictor of surviving a year. A proven
  term beats one that's merely new.

**Signs it's EPHEMERAL — skip it, or wait:**
- **You can't explain it without retelling the origin event** — that's a reference, not a word.
- **Tied to one incident / video / person**, funny only if you've seen the clip.
- **Stuck in one niche** — a single game's forum, one fandom — with no sign of spreading.
- **This week's format** that next week's will replace.

**The decision:** default to the enduring core. A niche or very fresh term goes in **only if** it both
fills a genuine gap **and** shows real signs of spreading and sticking. If you're unsure, **leave it out
and revisit later** — if it endures it'll still be there next month, and if it died you never needed it.
Two rock-solid words (or one) beat a batch padded with three that won't outlive the quarter.

## Entry schema (every field required)
```json
{
  "id": "kebab-case-unique-slug",
  "hanzi": "汉字 / term",
  "pinyin": "pīnyīn with tone marks",
  "literal": "morpheme-by-morpheme gloss",
  "meaning": "what it actually means and how it's used (English)",
  "meaning_zh": "the same explanation written in Mandarin (简体中文)",
  "example": "a natural example sentence in Chinese",
  "example_pinyin": "sentence pinyin with tone marks",
  "example_translation": "English translation",
  "context": "origin story: where it came from, which platform, why netizens use it",
  "category": "slang | social | meme | abbreviation | news | chengyu",
  "date_added": "YYYY-MM-DD",
  "sources": [
    { "url": "https://…", "note": "source name + what it is", "lang": "zh" }
  ]
}
```
`sources` is a JSON **array of one or more objects**, each the evidence behind the term and its
example. Every source object has three required fields:
- `url` — an http(s) link to the evidence.
- `note` — a short human citation (source name + what it is), in **Mandarin or English**.
- `lang` — `"zh"` or `"en"`, the language of the source.

Use the actual sources you verified the term against in step 4 — **copy the URL from a real search
result, never construct or guess one.** If you leaned on several, list them all. Sourcing is never
shown on the study card — it exists to keep entries verifiable and to be pulled out on export.
`add_words.py` rejects any entry whose `sources` is missing or malformed.

## Quality bar
- The `context` field is the point of the app — always explain the *origin/vibe*, not just the meaning.
- Keep examples short and idiomatic.
- Accuracy over volume: 3 solid terms beat 5 shaky ones. **Durability over novelty**: a proven word
  beats a buzzy one, and adding just 1–2 (or backfilling the enduring core) beats padding with fads.
- Every entry must carry at least one real `source` — no term ships unsourced.
- For meme-category entries, `meaning` should read as fact (what's actually going on) rather
  than a fabricated dictionary sense — it's fine for the "definition" to just be the joke/story.
