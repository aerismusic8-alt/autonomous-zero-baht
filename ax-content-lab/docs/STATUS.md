# AX Viral Content Lab — Status

Generated: 2026-10-14T23:47:54.737149+00:00  |  commit: `b7af0b9`

## Headline numbers (all evidence-backed)

- Videos produced: **30**
- Videos passing full QC: **30** (30/30)
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
| 0011_the_probe_that_came_back | Deep Space Logs | The Probe That Came Back | 25.08s | 16/16 | PASS | 3.2 MB |
| 0012_six_minutes_of_silence | Deep Space Logs | Six Minutes of Silence | 22.3s | 16/16 | PASS | 2.8 MB |
| 0013_the_long_orbit | Deep Space Logs | The Long Orbit | 24.74s | 16/16 | PASS | 3.1 MB |
| 0014_duplicate_transmission | Deep Space Logs | Duplicate Transmission | 22.48s | 16/16 | PASS | 2.8 MB |
| 0015_the_house_that_counts | Quiet Horror Files | The House That Counts | 25.09s | 16/16 | PASS | 3.2 MB |
| 0016_the_note_in_the_fridge | Quiet Horror Files | The Note in the Fridge | 23.14s | 16/16 | PASS | 2.9 MB |
| 0017_the_three_am_train | Quiet Horror Files | The 3 AM Train | 27.83s | 16/16 | PASS | 3.5 MB |
| 0018_the_extra_shadow | Quiet Horror Files | The Extra Shadow | 21.37s | 16/16 | PASS | 2.7 MB |
| 0019_the_speed_of_falling | Cosmic Wonders | The Speed of Falling | 20.45s | 16/16 | PASS | 2.8 MB |
| 0020_why_stars_die_twice | Cosmic Wonders | Why Stars Die Twice | 23.87s | 16/16 | PASS | 3.3 MB |
| 0021_the_coldest_place | Cosmic Wonders | The Coldest Place | 22.16s | 16/16 | PASS | 3.1 MB |
| 0022_the_sound_of_a_black_hole | Cosmic Wonders | The Sound of a Black Hole | 22.8s | 16/16 | PASS | 3.2 MB |
| 0023_the_vanished_village | Unsolved Archive | The Vanished Village | 25.09s | 16/16 | PASS | 3.5 MB |
| 0024_the_man_who_never_slept | Unsolved Archive | The Man Who Never Slept | 24.06s | 16/16 | PASS | 3.4 MB |
| 0025_the_tape_from_room_three | Unsolved Archive | The Tape from Room 3 | 22.28s | 16/16 | PASS | 3.2 MB |
| 0026_the_second_landing | Unsolved Archive | The Second Landing | 25.63s | 16/16 | PASS | 3.6 MB |
| 0027_if_you_stopped_time | What If Physics | If You Stopped Time | 25.59s | 16/16 | PASS | 3.3 MB |
| 0028_if_light_was_slow | What If Physics | If Light Was Slow | 22.11s | 16/16 | PASS | 2.9 MB |
| 0029_if_the_ocean_drained | What If Physics | If the Ocean Drained | 21.85s | 16/16 | PASS | 2.8 MB |
| 0030_if_you_could_see_radio | What If Physics | If You Could See Radio | 24.55s | 16/16 | PASS | 3.2 MB |

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
- `research/references_20261014T183329Z.json`
- `research/references_20261014T183519Z.json`
- `research/references_20261014T183835Z.json`
- `research/shorts_scan_20261014T151740Z.json`

## Repository

- GitHub: https://github.com/aerismusic8-alt/autonomous-zero-baht/tree/ax-content-lab/ax-content-lab
- Public — all code, QC reports, specs, research snapshots and the 30 finished
  MP4s are readable without authentication.
- Sync with `bash pipeline/sync_repo.sh` (reads `secrets/github_pat.txt`).

## Publishing channels

| Platform | Ready | Missing credential |
|---|---|---|
| YouTube | BLOCKED | youtube_client_secret.json, youtube_token.json |
| TikTok | BLOCKED | tiktok_client.json, tiktok_token.json |
| Facebook | BLOCKED | meta_client.json, meta_token.json |
| Instagram | BLOCKED | meta_client.json, meta_token.json |


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
5. Produced 30 original videos, all with original writing, original procedural music, and original procedural visuals — zero third-party assets.
6. Quality-checked every one: 30/30 passed 16/16 checks including real frame analysis, silence detection and loudness measurement.
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
