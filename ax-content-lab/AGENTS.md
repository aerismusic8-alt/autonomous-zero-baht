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
  **As of 2026-10-19 the token is valid and write-scoped**: `check` reports
  `authenticated: true`, `login: aerismusic8-alt`, `can_push: true`. PERSIST is
  no longer blocked. Do not trust the environment `$GITHUB_TOKEN` (still empty
  here) — use the file, or embed it: `TOK=$(tr -d '\n\r' < secrets/github_pat.txt)`.
- **Sync**: `bash pipeline/sync_repo.sh` — fast-forwards the remote branch, force-adds
  `final.mp4` and `brand/*.png` (they are gitignored but must stay tracked as evidence),
  never commits `secrets/`.
- **PR creation is blocked**: the PAT lacks "Pull requests: write"
  (`Resource not accessible by personal access token`). The branch itself is public
  and readable, which is enough. To open PRs, add that permission to the PAT.
- **YouTube upload**: BLOCKED — no OAuth token. This sandbox has no browser, so
  K must mint a token via Google OAuth Playground and hand it over with
  `connect.py youtube-token` (see `docs/SETUP_FOR_K.md`). Then
  `publisher.py --all --privacy private` works.
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
  command text. Reference `$GITHUB_TOKEN` explicitly when you need it. (Not
  guaranteed in every runtime — see "Loop operations" below.)

## Loop operations (agent gotchas — learned the hard way)

- **Long renders must run in the background.** This runtime caps foreground
  commands (~1080 s) and idle-cleans at ~1200 s, so a `--timeout 3100` batch is
  refused. Run `nohup python3 pipeline/batch.py --workers 3 > /tmp/batch.log 2>&1 &`
  and poll the log with short sleeps. A backgrounded command must be the *whole*
  command string — do not chain a second command after `&`; use `;`/`&&`.
- **Exit codes lie.** `publisher.py`, `multipost.py`, `analytics.py`, `store.py`,
  `report.py` all exit 0 even when the result is `BLOCKED`/`ok:false`. Judge
  success from the printed JSON payload (`ok`, `blocked`, `status`), never the
  exit code alone.
- **Token availability varies per runtime.** AGENTS.md says secrets inject when
  the key name appears in the command, but in this sandbox both `$GITHUB_TOKEN`
  and the auto-injected secret can be stale/empty; the file at
  `secrets/github_pat.txt` is the one that works. Never hardcode the runtime
  hostname (it changes every session) — `serve.py` derives it from
  `PUBLIC_URL`/`RUNTIME_URL`, so docs must say "use the URL serve.py prints",
  not paste a literal URL.
- **`publisher.py` needs a browser** (`flow.run_local_server`). This sandbox has
  none, so the working path is Google OAuth Playground → `connect.py
  youtube-token`. Do not tell K to just run `publisher.py --all` here and expect
  consent to complete.
- **Docs drift fast.** After changing credential state, grep all of `docs/` and
  `AGENTS.md` for the old status (`grep -rn "BLOCKED" docs/ AGENTS.md`) — three
  docs disagreed about whether PERSIST was blocked, which confused K. Keep
  `SETUP_FOR_K.md`, `K_ACTION_PLAN.md`, `POST_ONE_CLIP.md` and `AGENTS.md`
  consistent; prefer pointing to one canonical walkthrough over duplicating it.
- **Missing deps masquerade as credential blockers.** `publisher.py` raised
  `ModuleNotFoundError: googleapiclient` for all 40 items; only after installing
  `google-api-python-client` did the real "OAuth client not found" appear. Fix
  the dependency before reporting a publish blocker.
- **`analyze.py` concatenates every snapshot**, not just the newest, despite the
  output filename `analysis_latest.md`. Expect one `## Snapshot:` block per
  `research/*.json` with a `queries` key.
- **`publisher.py` needs `googleapiclient` installed, or the failure is a red
  herring.** A fresh runtime reported `ok:false, error: ModuleNotFoundError: No
  module named 'googleapiclient'` for all 40 pieces — that is a missing dep, not
  the real blocker. Install `google-api-python-client google-auth-oauthlib`, then
  re-run: the genuine message is the `BLOCKED: YouTube OAuth client secret not
  found ...` one. Always fix deps before reporting a publish blocker.
- **Verifying new work:** compare each new spec's keys against the newest existing
  spec (currently `spec_0035`) for exact top-level/scene/packaging parity; confirm
  `provenance.third_party_assets == []`; count QC PASS by reading every
  `content/*/qc_report.json` directly rather than trusting `batch_summary.json`.

## Current status

**PROJECT STOPPED BY OPERATOR (2026-10-19).** K requested the lab be closed down.
A kill switch is in place: the file `STOP` at the lab root makes every production
entrypoint (`run_loop.sh`, `pipeline/batch.py`, `pipeline/produce.py`,
`pipeline/gen_specs.py`) exit immediately without writing anything. Delete `STOP`
to resume. No new content is being produced. The 65 finished pieces remain on disk
and in the public repo as evidence.

65 videos produced, 65/65 QC PASS (independently re-verified spec-compliant).
Newest: specs 0061–0065 (one per series), all rendered and QC PASS.
0 published (BLOCKED on credentials for all four platforms). Revenue ฿0.00.
Reference research: real high-view videos with links in `site/references.html`.

**Still needs K to fully close down:**

1. **The OpenHands automation that drives this loop is still scheduled.** The loop
   iteration is started by an OpenHands automation (env `AUTOMATION_SESSION_URL`),
   not by GitHub Actions. With `STOP` in place a run now does nothing, but the
   automation keeps firing. K should disable/delete that automation in OpenHands.
2. **The `Zero-Baht Foundation` GitHub Actions workflow is still scheduled** (cron
   every 6 h on `main`; 71 runs so far). The supplied PAT lacks the Actions
   permission, so it cannot be disabled via the API (`403 Resource not accessible`).
   K must disable it in the repo's Actions tab, or remove the workflow file.
3. **Publishing was never enabled and is now moot** — one OAuth/API credential per
   platform was required; none was ever supplied, so 0 videos were published.

**PERSIST is PARTIALLY RESOLVED (2026-10-19).** K supplied a fine-grained PAT with
Contents write, so `sync_repo.sh` pushes code + evidence. It does NOT have the
fine-grained **Workflows** permission, so GitHub rejects any push that touches
`.github/workflows/` — and that rejection is atomic, it would also drop the code.
`sync_repo.sh` now detects that, retries without workflow changes, and reports the
workflow blocker separately. As a result the CI workflow at the repo root is still
NOT installed, so the lab does not yet run in Actions. To fix: grant the PAT
`Workflows: Read and write` (docs/SETUP_FOR_K.md item 1), then re-run the sync.
Push the lab with `bash pipeline/sync_repo.sh` at the end of every loop.

**CI blocker (2026-10-19).** GitHub Actions only reads `.github/workflows/` at the
REPOSITORY ROOT, so `ax-content-lab/.github/workflows/lab-loop.yml` never runs.
`sync_repo.sh` installs the canonical workflow at the root, but the token's missing
Workflows permission blocks that file from being pushed. The scheduled crons in that
workflow are additionally inert until the default branch contains it (schedules only
fire for workflows on the default branch, which is `main`). The active autonomous
trigger will be the `push` event on `ax-content-lab` once the workflow lands.

One blocker still needs K (see `docs/SETUP_FOR_K.md` and `docs/K_ACTION_PLAN.md`):

1. **Publish is BLOCKED.** One OAuth/API credential per platform (YouTube OAuth
   client; TikTok client + token; Meta token for FB/IG Reels). No anonymous
   upload path exists and none is attempted. Until a credential lands,
   `publisher.py` prints `BLOCKED: YouTube OAuth client secret not found ...` and
   every publication count stays 0.

## Status vocabulary

`VERIFIED` / `IN PROGRESS` / `PENDING VERIFICATION` / `BLOCKED` / `ASSUMPTION`.
Revenue stages: `REPORTED → VERIFIED → BALANCE AVAILABLE → PAYOUT ELIGIBLE → CASH RECEIVED`.
