# AX Viral Content Lab — Status

Generated: 2026-10-14T18:26:04.713339+00:00  |  commit: `62cd22a`

## Headline numbers (all evidence-backed)

- Videos produced: **10**
- Videos passing full QC: **10** (10/10)
- Videos published: **0**
- Verified audience metrics captured: **0**
- Verified revenue: **฿0.00** (no payout channel is active yet)

## Content inventory

| Slug | Series | Title | Duration | QC | QC status | Size |
|---|---|---|---|---|---|---|
| 0001_the_last_signal | Deep Space Logs | The Last Signal | 23.5s | 16/16 | PASS | 3.0 MB |
| 0002_the_lighthouse_log | Quiet Horror Files | The Lighthouse Log | 27.54s | 16/16 | PASS | 3.4 MB |
| 0003_voyagers_silence | Deep Space Logs | Voyager's Silence | 24.29s | 16/16 | PASS | 3.0 MB |
| 0004_the_map_that_shouldnt_exist | Unsolved Archive | The Map That Shouldn't Exist | 22.49s | 16/16 | PASS | 3.2 MB |
| 0005_if_the_sun_blinked | What If Physics | If the Sun Blinked | 22.13s | 16/16 | PASS | 2.9 MB |
| 0006_the_second_guest | Quiet Horror Files | The Second Guest | 22.6s | 16/16 | PASS | 2.8 MB |
| 0007_signal_from_kepler | Deep Space Logs | Signal from Kepler | 25.16s | 16/16 | PASS | 3.1 MB |
| 0008_why_nothing_is_empty | Cosmic Wonders | Why Nothing Is Empty | 22.54s | 16/16 | PASS | 3.1 MB |
| 0009_the_last_photo | Unsolved Archive | The Last Photo | 21.4s | 16/16 | PASS | 3.0 MB |
| 0010_if_you_fell_through_earth | What If Physics | If You Fell Through Earth | 22.92s | 16/16 | PASS | 3.0 MB |

## Publication status

**BLOCKED — 0 published.**

Reason: every platform requires a user-authorised OAuth token to upload. AX has written and tested the YouTube uploader (`pipeline/publisher.py`) up to that boundary; it cannot cross it without K creating a free Google Cloud OAuth client. Exact steps: `docs/PUBLISHING.md`.

## Revenue

| Stage | Amount | Evidence |
|---|---|---|
| REPORTED | ฿0.00 | none |
| VERIFIED | ฿0.00 | none |
| BALANCE AVAILABLE | ฿0.00 | none |
| PAYOUT ELIGIBLE | ฿0.00 | none |
| CASH RECEIVED | ฿0.00 | none |

No revenue stage is claimed beyond REPORTED=0 because no monetisation channel is active. Prerequisites AX has verified: YouTube Partner Program needs 1,000 subscribers + 4,000 public watch-hours (or 10M Shorts views) — none of which can be assessed before publishing starts.

## Research evidence

- `research/loop_20261014T155507Z.json`
- `research/niche_scan_20261014T151544Z.json`
- `research/shorts_scan_20261014T151740Z.json`

## Repository

- GitHub: https://github.com/aerismusic8-alt/autonomous-zero-baht/tree/ax-content-lab/ax-content-lab
- Public — all code, QC reports, specs, research snapshots and the 10 finished
  MP4s are readable without authentication.
- Sync with `bash pipeline/sync_repo.sh` (reads `secrets/github_pat.txt`).

## Automation

- GitHub Actions workflow: `.github/workflows/lab-loop.yml` (2×/day, free minutes).
- OpenHands automation: **AX Content Lab - Daily Production Loop**, cron `0 7 * * *` UTC, enabled.
  It runs the loop, writes 5 new original specs, produces + QC-checks, and reports honestly.
- Local one-shot: `./run_loop.sh`.
- Every run is idempotent: already-produced pieces are skipped (see `produce.build(force=False)`).

## Channel assets ready for K

- `brand/avatar.png` (66 KB)
- `brand/banner.png` (171 KB)
- `brand/endcard.png` (159 KB)

## What AX completed autonomously

1. Verified the real environment and built a free/open-source toolchain (`docs/TOOLS.md`).
2. Collected real public market data and stored raw evidence (`research/*.json`).
3. Analysed it and selected niches with documented rationale (`docs/MARKET_RESEARCH.md`).
4. Built an end-to-end original production pipeline (research → script → assets → voice/music → edit → QC → package).
5. Produced 10 original videos, all with original writing, original procedural music, and original procedural visuals — zero third-party assets.
6. Quality-checked every one: 10/10 passed 16/16 checks including real frame analysis, silence detection and loudness measurement.
7. Built the publishing, analytics and state layers and a free continuous scheduler.

## BLOCKED / needs K

| Item | Why AX cannot do it | Action needed |
|---|---|---|
| Platform upload | Requires OAuth token bound to K's identity | Create Google Cloud OAuth client → `secrets/youtube_client_secret.json` (5 min, free) |
| Channel creation | Requires K's Google account identity | Create the channel, then tell AX the name |
| Monetisation enrolment | Requires identity, tax and bank details | Only after publishing + eligibility |

Nothing else is blocked. Everything above the publishing line runs unattended.

## Next actions (automatic unless blocked)

1. Run the loop on schedule (GitHub Actions + OpenHands automation).
2. On first OAuth token, upload all QC-passed items as private and verify playback.
3. Capture first real audience metrics, then run the A/B experiments in `data/experiments.json`.

## Status vocabulary used

- **VERIFIED** — proven by a real artifact or platform response.
- **PENDING VERIFICATION** — produced, awaiting platform confirmation.
- **IN PROGRESS** — currently running.
- **BLOCKED** — needs an external action (see table above).
- **ASSUMPTION** — untested belief listed in `docs/MARKET_RESEARCH.md` §6.
