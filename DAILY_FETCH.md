# Daily netizen-vocab fetch — agent recipe

This is the task the scheduled agent runs each morning to grow `vocab.json`.

## Goal
Find 3–5 **fresh, genuinely-trending** Chinese netizen terms and append them to `vocab.json`,
never duplicating a term already in the file.

## Steps
1. **Read** `vocab.json` and collect every existing `hanzi` and `id` so you can skip duplicates.
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
5. **Append** each as an object to the `vocab.json` array with ALL fields below, then confirm
   the file is still valid JSON.
6. Commit with a message like `vocab: add N terms (YYYY-MM-DD)` (once the project is in git).

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
