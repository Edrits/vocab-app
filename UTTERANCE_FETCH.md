# Utterance-glossary fetch — agent recipe

How to research and add entries to the **口头禅 · utterance glossary** (the
`utterances` collection in `reference.json`, reached from the ☰ sidebar in the app).

This is **not** the daily netizen-vocab task. `vocab.json` collects *trending* terms;
this collects the **stable connective tissue of everyday speech** — the fillers, tags,
reactions and sentence-joiners real people say out loud but textbooks rarely define.
The two must not overlap: a fresh meme belongs in `vocab.json`, a durable spoken
particle belongs here.

## Goal
Add 3–5 genuine **spoken-discourse expressions** per batch, each one verified against
real usage, never duplicating an entry already in the collection. Quality of the
**register/usage note** is the whole point — see the quality bar.

## The bar that defines this collection: *outside dictionary Mandarin*
We specifically want the things a learner only picks up by immersion. Before adding
anything, apply this test:

- **Would an HSK textbook or a standard 词典 teach this as a defined word with a clean
  gloss?** If yes, it's probably too "dictionary" for here — skip it. (拒绝, 因为, 但是
  are dictionary Mandarin. 得了吧, 那什么, 属于是, 完了 are not.)
- **Is it doing a *conversational job* rather than carrying dictionary meaning?** The
  best entries are pragmatic, not semantic: opening a turn, stalling for a word,
  softening a refusal, backchanneling, changing the subject, expressing exasperated
  agreement, winding a call down. The literal meaning is often nothing like the use
  (可不是嘛 looks negative, means emphatic yes; 你别说 means "don't say" but concedes a
  point).
- **Do real people actually *say* it?** Not "is it grammatical" — is it attested in
  unscripted speech and casual writing. If you can't find it being used naturally, drop it.

Good hunting grounds *within* the bar: hesitation fillers (那什么, 就是说吧, 怎么说呢),
turn-openers (我跟你讲, 说真的), backchannels and reactions (可不是嘛, 得了吧, 不至于吧,
你别说), sentence-final particle combos that shift tone (行吧 vs 好吧, 了吧, 呗, 嘛),
discourse tags (属于是, 就离谱, 完了), softeners and pre-apologies (不是我说, 有点那个),
and closers (算了, 就这样吧, 差不多得了).

## Where to actually research (real speech, not dictionaries)
Dictionaries are for *checking* an entry, not for *finding* one — by definition the
good ones are under-documented. Go where unscripted Mandarin lives, and **rotate
sources** so entries stay varied:

- **Unscripted video** — Douyin / Bilibili / RedNote vlogs, street interviews (街采),
  and especially variety shows and reality TV (《再见爱人》, 脱口秀 / stand-up, talk
  shows). Scripted drama is weaker; you want people talking, not acting a script.
- **Comment sections & 弹幕** (评论区, danmu) — written but spoken in register; this is
  where 得了吧, 不至于吧, 属于是, 就离谱 swarm.
- **Podcasts (播客)** — long stretches of casual unscripted chat; great for connectives.
- **Native-speaker explainers** — 知乎 / 小红书 / Bilibili posts where Chinese speakers
  themselves unpack "为什么大家老说 X" or "X 是什么意思". These both surface expressions
  *and* explain the pragmatics — but they're opinions, so corroborate.
- **Colloquial reference for verification** — 现代汉语词典 marks spoken items 〈口〉;
  汉典 / 百度百科 / 沪江, and dictionaries of 惯用语 (idiomatic colloquialisms) and 口语,
  confirm a sense once you've found the expression in the wild.

Search-string patterns that work: "汉语 口头禅 大全", "中国人说话 口语 连接词", "X 是什么意思
口语", "为什么 中国人 老说 X", "spoken Chinese discourse markers / filler words", plus the
platform name (Bilibili / 小红书) to pull real usage rather than textbook lists.

## Technique: hunt by function, not by word
The reliable way to find non-dictionary items is to **pick a conversational job first**,
then go find how real speakers do it:
1. Choose a gap — e.g. "how do people stall while thinking?", "how do they half-agree?",
   "how do they end a call without anything being wrong?", "how do they soften a
   correction?". Check the collection's five groups (getting started / keeping it going /
   reacting / softening / wrapping up) for which are thin.
2. Watch/read real speech doing that job and note the recurring phrase.
3. Verify it's a *pattern*, not one person's tic, and pin down the register.

## Verify, and record real usage evidence (`sources` — required)
For every candidate, confirm the meaning **and the register** against real usage before
writing it — do not invent pragmatics. Then record where you saw it in the entry's
`sources` array. For an utterance a source is **usage evidence** — a clip, a comment
thread, a native-speaker explainer, an 〈口〉 dictionary entry — that shows the phrase is
really said this way. **Copy each URL from a real search result; never construct or guess
one.** If a candidate is only ever one creator's catchphrase, or you can't corroborate the
register, drop it rather than guess. (The 25 entries that predate this recipe were added by
hand and carry no `sources`; that's fine — new ones must.)

## Regional & register flags
Colloquial speech is marked. Where relevant, say so in the `note`:
- **Region** — 我寻思, 那可不 are northern; some softeners are more southern. Flag it.
- **Register / edge** — casual-only, mildly rude, passive-aggressive, only-among-friends.
  Tone often flips the meaning (然后呢 as genuine interest vs. flat sarcasm; 算了 as
  generous vs. resigned). The note must capture that.
- **Freshness** — if it's really a fleeting meme rather than durable spoken habit, it
  belongs in `vocab.json` (category `meme`), not here.

## Append via the script (never hand-edit reference.json)
Draft your new entries as a JSON array to a scratch file *outside the repo*
(e.g. `$TMPDIR/new_utterances.json`), then run:
```
python3 scripts/add_utterances.py "$TMPDIR/new_utterances.json"
```
It validates the schema, confirms each `group` exists, dedupes on `hanzi`, appends the
rest, and prints per-group totals. (Add `ran` as a second argument to target the 然-combos
collection instead.) Fix and re-run on schema errors — never edit `reference.json` directly.

Then commit `reference.json` with a message like `reference: add N utterances (YYYY-MM-DD)`
and push (push to `main` = deploy via GitHub Pages).

## Entry schema (every field required)
```json
{
  "hanzi": "口头禅 / phrase",
  "pinyin": "pīnyīn with tone marks",
  "gloss": "short English gloss — what it does, not a literal translation",
  "group": "opening | linking | reacting | hedging | closing",
  "note": "the pragmatics: when it's used, how it lands, tone/region sensitivity, and how it differs from a near-neighbour",
  "example": "a natural utterance or mini-exchange in Chinese (—A —B is ideal)",
  "example_pinyin": "example pinyin with tone marks",
  "example_translation": "idiomatic English translation",
  "blend": "OPTIONAL — how the characters slur together in fast speech (see below)",
  "sources": [
    { "url": "https://…", "note": "where it's really used — clip / thread / 〈口〉 entry", "lang": "zh" }
  ]
}
```
The `group` values map to the sections in order — `opening` (开口 · Getting started),
`linking` (接话 · Keeping it going), `reacting` (反应 · Reacting), `hedging` (缓冲 ·
Softening it), `closing` (收尾 · Wrapping up), `frame` (句式 · Spoken frames) and
`fast` (连读 · Said fast). Pick the section by the phrase's conversational *function*.

- **`frame`** is for spoken sentence patterns with a slot — 怎么也……不, 再……也……,
  说什么也……, 爱……不……. Write the `hanzi` with `……` marking the gap, and put a filled
  example in `example`. These carry emphasis/attitude a textbook frame (无论…都) doesn't.
- **`fast`** is for words that *are* a run-together contraction — 酱紫 (这样子), 不造
  (不知道), 甭 (不用), 咋 (怎么). The blend is the point, so spell out the parent phrase.

## The optional `blend` field
Set `blend` when a phrase is habitually **slurred in quick speech** so it doesn't sound like
its written form — e.g. 那什么 → 'nàshém', 怎么也 → 'zěm-yě'. Keep it one short line, and
give the approximate run-together sound. It renders as a distinct "Said fast" row in the app,
and it's searchable. Leave it off when there's nothing notable — most entries won't need it;
it's exactly what learners miss when they can read a phrase but can't catch it in the wild.

## Quality bar
- **The `note` is the product.** Write pragmatics, not a dictionary gloss: the situation,
  the tone, who says it to whom, what it really signals. If it reads like a 词典 entry,
  it's wrong for this collection.
- **Contrast the near-neighbours** — like the 然-combos notes do. Adding 行吧? Say how it
  differs from 好吧. Adding 就是说? Contrast 也就是说. This is what makes the glossary teach.
- **Examples should sound spoken** — short, idiomatic, ideally a two-line exchange showing
  the turn it belongs in, not a textbook sentence.
- **Every new entry carries at least one real `source`.** No unsourced additions.
- **Accuracy over volume** — 3 well-observed, well-sourced entries beat 5 guessed ones.
- **Stay out of `vocab.json`'s lane** — durable spoken habits here; trending slang there.
