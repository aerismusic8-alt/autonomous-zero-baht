# AGENTS.md — AX Viral Content Lab

Persistent memory for agents working in this repository. Read this first.

## What this is

An autonomous, zero-cost content studio (฿0 budget). It researches a market,
writes **original** short-form stories, renders them into finished vertical
videos with original procedural music and free neural narration, quality-checks
the rendered files, and is wired to publish and measure.

## Hard rules (do not violate)

1. Free tier / open source only. No paid APIs, credits, ads, VPS, or subscriptions.
   Never spend money without explicit approval from K.
2. Do not claim a video is published without a real platform ID that the API can
   re-read. Do not claim revenue that is not `CASH RECEIVED`.
3. Never create fake/duplicate accounts, never evade CAPTCHA/KYC, never use
   stolen credentials. Platform auth requires K.
4. Never reuse third-party footage, music, scripts, or images. All content must be
   original. `metadata.json.provenance.third_party_assets` must stay empty.
5. Never commit secrets. `secrets/` is git-ignored (mode 700).

## Environment (verified 2026-10-14)

Debian 13, 4 vCPU, 15 GB RAM, 25 GB disk, `sudo` available, outbound network OK.

Installed toolchain (all free):
`ffmpeg` `ffprobe` `sqlite3` `imagemagick` + pip: `yt-dlp` `edge-tts` `Pillow`
`numpy` `google-api-python-client` `google-auth-oauthlib`.

`~/.local/bin` must be on PATH (add `export PATH="$HOME/.local/bin:$PATH"`).

## Commands

```bash
./run_loop.sh                                   # full loop end to end
python3 pipeline/research.py --queries "..."    # market research -> research/*.json
python3 pipeline/analyze.py                     # patterns table
python3 pipeline/gen_specs.py                   # write content specs
python3 pipeline/batch.py --workers 3           # produce + QC in parallel (idempotent)
python3 pipeline/batch.py --force               # rebuild everything
python3 pipeline/store.py sync                  # refresh SQLite state
python3 pipeline/publisher.py --dry-run         # validate packages
python3 pipeline/publisher.py --all             # upload to YouTube (needs OAuth)
python3 pipeline/multipost.py --status          # real credential status, per platform
python3 pipeline/multipost.py --all             # upload to every ready platform
python3 pipeline/schedule.py --show             # posting plan and queue depth
python3 pipeline/schedule.py --tick             # post the due slot (idempotent)
python3 pipeline/verify_all.py                  # independent spec re-verification
python3 pipeline/references.py                  # real high-view references + links
python3 pipeline/build_refs_page.py             # render site/references.html
python3 pipeline/analytics.py                   # pull real stats
python3 pipeline/report.py                      # regenerate docs/STATUS.md
python3 pipeline/build_site.py                  # rebuild the public gallery
bash pipeline/sync_repo.sh                      # push code + evidence to GitHub
python3 pipeline/connect.py check               # verify credentials (real write probe)
```

## Pipeline contract

`pipeline/produce.py` reads `content/specs/*.json` and writes
`content/<slug>/{final.mp4,thumbnail.png,metadata.json,qc_report.json,assets/}`.

A piece is only "done" when `qc_report.json.status == "PASS"` (16 checks,
including real frame brightness/variance, silence detection, loudness).
Do not lower QC thresholds to hit a count — report produced vs. passed separately.

## Repository and publishing state

- **GitHub repo**: https://github.com/aerismusic8-alt/autonomous-zero-baht (public),
  lab lives on branch `ax-content-lab` under `ax-content-lab/`.
- **Write token**: stored at `secrets/github_pat.txt` (mode 600, git-ignored).
  A fine-grained PAT does NOT report `x-oauth-scopes`; verify write ability with
  the real probe in `pipeline/connect.py check` (`can_push: true`).
- **Sync**: `bash pipeline/sync_repo.sh` — fast-forwards the remote branch, force-adds
  `final.mp4` and `brand/*.png` (they are gitignored but must stay tracked as evidence),
  never commits `secrets/`.
- **PR creation is blocked**: the PAT lacks "Pull requests: write"
  (`Resource not accessible by personal access token`). The branch itself is public
  and readable, which is enough. To open PRs, add that permission to the PAT.
- **YouTube upload**: still BLOCKED — no OAuth client. Needs K.
- **Multi-platform posting**: `pipeline/platforms.py` reads credential files on disk and
  reports per-platform readiness. `multipost.py` uploads; `schedule.py --tick` posts one
  queued item per ready platform at 09/13/18/21 local (UTC+7). A publication row is
  written only when the platform returns a real id/url — otherwise the run is BLOCKED.
  All four platforms (YouTube, TikTok, Facebook Reels, Instagram Reels) need a
  user-authorized token; there is no anonymous upload path, and none is attempted.
- **Credential intake**: `pipeline/serve.py` serves a gallery plus `/connect`, where K
  can paste a token over HTTPS without it entering the chat log. It accepts GitHub,
  YouTube client JSON, TikTok client JSON, and Meta token JSON.

## Performance notes

- One video takes ~90–160 s wall clock; rendering is CPU-bound.
- `batch.py --workers 3` is the sweet spot on 4 vCPU (3 workers ≈ 25 min for 30 videos).
- A no-op batch run is <1 s because finished work is skipped.
- `edge-tts` needs network. `yt-dlp` search works but can rate-limit; treat failures
  as non-fatal (`|| true`).

## Known constraints / gotchas

- `metadata=print` from ffmpeg writes to stdout, not stderr — QC uses PIL frame
  extraction instead. Do not revert that.
- Scene fades only on the first and last scene (`fade_start`/`fade_end`), otherwise
  the concat produces black flashes between scenes.
- `git add -A` alone will not stage `final.mp4` (gitignored); the sync script
  force-adds it. Do not `rm` the videos from disk — that stages a deletion.
- YouTube upload quota ≈ 10,000 units/day ≈ 6 uploads/day. Keep ≤6/day.
- Secrets are injected into a command only when the secret key name appears in the
  command text. Reference `$GITHUB_TOKEN` explicitly when you need it.

## Current status

30 videos produced, 30/30 QC PASS (independently re-verified spec-compliant),
pushed to the public repo. 0 published (BLOCKED on credentials for all four
platforms). Revenue ฿0.00. The one action needed from K: an OAuth/API credential
per platform → see `docs/SETUP_FOR_K.md`. Reference research: 95 real high-view
videos with links in `site/references.html`.

## Status vocabulary

`VERIFIED` / `IN PROGRESS` / `PENDING VERIFICATION` / `BLOCKED` / `ASSUMPTION`.
Revenue stages: `REPORTED → VERIFIED → BALANCE AVAILABLE → PAYOUT ELIGIBLE → CASH RECEIVED`.
