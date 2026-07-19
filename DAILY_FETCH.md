# Daily netizen-vocab fetch — agent recipe

This is the task the scheduled agent runs each morning to grow `vocab.json`.

## Goal
Find 3–5 **fresh, genuinely-trending** Chinese netizen terms and append them to `vocab.json`,
never duplicating a term already in the file.

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
2. **Search** current Chinese internet trends. Rotate across sources so results stay varied:
   - Weibo hot search (微博热搜), Douyin / RedNote (小红书) trending, Bilibili
   - "中国 网络流行语 <current month/year>", "trending Chinese internet slang <year>"
   - current-news and meme terms netizens are actually using this week
3. **Select** 3–5 terms that are (a) not already in the deck, (b) genuinely in use — not
   textbook words, (c) explainable with real cultural context. Prefer a mix of categories.
   - **Chengyu rule:** include roughly **one classic chengyu (成语) per ~10 new words added**.
     Prefer chengyu that still circulate in online/comment culture, and in the `context`
     field note how netizens actually use it. Use category `chengyu`. Don't force one into
     every batch — track the running ratio (about 1 in 10).
4. For each term, **verify meaning/usage** against at least one source before writing it —
   do not invent definitions. If unsure about a term, drop it rather than guess.
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
  "date_added": "YYYY-MM-DD"
}
```

## Quality bar
- The `context` field is the point of the app — always explain the *origin/vibe*, not just the meaning.
- Keep examples short and idiomatic.
- Accuracy over volume: 3 solid terms beat 5 shaky ones.
