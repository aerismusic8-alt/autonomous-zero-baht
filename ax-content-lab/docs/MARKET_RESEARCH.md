# Market Research — AX Viral Content Lab

All numbers below come from **public YouTube metadata** collected by
`pipeline/research.py` (yt-dlp). Raw evidence is stored verbatim in
`research/*.json` with the collection timestamp. View counts are used as a
*signal of audience interest only* — they are **not** treated as proof of income
(project rule 4).

- Collection date: **2026-10-14**
- Method: `yt-dlp ytsearch` + per-video metadata (read-only, no media downloaded)
- Snapshots: `research/niche_scan_20261014T151544Z.json`, `research/shorts_scan_20261014T151740Z.json`

## 1. What the data shows

| Niche query | Results | Median views | Max views | Median length | Shorts <60s |
|---|---|---|---|---|---|
| ai animated short story | 20 | 473,356 | 94,854,639 | 880 s | 0/20 |
| scary story animated shorts | 20 | 581,095 | 7,001,817 | 2,521 s | 0/20 |
| space facts shorts | 20 | 865,054 | 15,244,146 | 1,154 s | 0/20 |
| history facts shorts | 20 | 784,282 | 11,624,269 | 833 s | 0/20 |
| scary stories shorts | 25 | 2,039,209 | 22,399,323 | 506 s | 0/25 |
| creepy facts shorts | 25 | 380,184 | 12,194,819 | 1,335 s | 0/25 |
| psychological facts shorts | 25 | 268,667 | 35,194,865 | 543 s | 0/25 |
| mystery story shorts | 25 | 1,817,109 | 12,846,509 | 1,056 s | 0/25 |
| what if shorts | 25 | 460,517 | 14,616,244 | 480 s | 3/25 |

## 2. Recurring patterns AX extracted

These are the structural lessons used to design our format. They are patterns,
not copies — no plot, script, or asset from any source is reused.

1. **Category, not platform, drives demand.** Story-driven categories
   (scary/mystery) show the highest medians (2.0M and 1.8M) even though the word
   "shorts" was in the query. Audience intent beats format labelling.
2. **Narrow, repeatable premise wins.** Channels that recur ("Top 3 stories…Part 10",
   "Deep Space Logs"-style entries) build returning audiences. Series > one-offs.
3. **A twist in the final beat is the dominant engagement mechanic.** Nearly every
   top performer resolves on a reversal ("sound fake but are 100% real",
   "…That Turned Out to Be True", "The Scariest…").
4. **Facts need a "fear/awe" frame.** Pure facts underperform; facts framed as
   unsettling or awe-inducing reach 3–15M ("Space is Terrifying", "30+ Facts Made
   Me a Bit Scared of Space").
5. **Titles use a curiosity gap, not a summary.** "What If They Never Met?",
   "The Shortest War EVER", "Ignore It".
6. **The 20–40 s vertical slot is the least contested.** The literal "shorts"
   queries returned long-form compilations (median 480–2,521 s), meaning short
   vertical narrative is comparatively underserved while demand for the
   *category* is proven.

## 3. Market gaps AX is targeting

| Gap | Evidence | Our play |
|---|---|---|
| Story-driven vertical micro-fiction is thin while the category is huge | "scary stories shorts" median 2.0M, but almost no results are true <60 s verticals | Short vertical original stories with a twist |
| Science "awe" framing works, but few series are vertical & serialised | space facts median 865k, max 15M; results are 15–180 min | Serialised 20–35 s vertical "what if" physics |
| Mystery/archive framing pulls large audiences but is dominated by long video essays | mystery median 1.8M | 25–35 s vertical "archive file" format |
| Little competition on original, rights-clean AI-assisted micro-fiction | top results are studios/compilations, not solo original series | Fully original writing + original procedural visuals = clean rights |

## 4. Niche selection (decision + rationale)

AX starts with **one primary niche and two backups**, all produced by the same
pipeline so switching costs almost nothing.

**Primary — Original micro-fiction with a twist** (series: *Deep Space Logs*,
*Quiet Horror Files*).
Rationale: highest median demand in the data, the twist mechanic is the single
most repeatable engagement pattern, it needs no factual claims (so no accuracy
risk), and it is 100% original writing — zero licensing exposure.

**Backup 1 — Cosmic / "what if" science awe** (*Cosmic Wonders*, *What If Physics*).
Rationale: second-highest ceiling (15M+), "awe framing" pattern is well supported,
and these are evergreen and cheap to script from verified physics.

**Backup 2 — Unsolved archive / mystery** (*Unsolved Archive*).
Rationale: strong median (1.8M) and the "file" format builds a returning audience.
Deferred because it requires careful factual sourcing to avoid defamation/accuracy
risk, so it is held as a later expansion.

## 5. Decision log

- 2026-10-14 — Chose primary niche per above. Rationale recorded here; raw data in `research/`.
- 2026-10-14 — Chose 20–35 s vertical format (least-contested slot, platform-agnostic).
- 2026-10-14 — Chose procedural visuals over generative AI (see `docs/TOOLS.md`).
- 2026-10-14 — Chose to keep view counts as *signal only*, never as income evidence.

## 6. What is still an ASSUMPTION

- That public YouTube demand transfers to TikTok/Reels/Shorts traffic. **ASSUMPTION** — must be tested after publishing.
- That a 20–35 s length maximises completion on Shorts. **ASSUMPTION** — to be A/B tested (see `data/experiments`).
- That the twist format sustains a series beyond ~10 entries. **ASSUMPTION**.
