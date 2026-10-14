# AX VIRAL CONTENT LAB

An autonomous, zero-cost content studio. It researches a market, writes original
short-form stories, renders them into finished vertical videos with original
procedural music and neural narration, quality-checks them, and is wired to
publish and measure — with an honest boundary at the one step that legally
requires a human: platform authorisation.

**Current state: 10 original videos produced and QC-passed (16/16 checks each).
0 published — blocked on platform OAuth, see [`docs/STATUS.md`](docs/STATUS.md).**

## Why this repo is honest

Most "AI content farm" projects claim more than they can prove. This one only
claims what it can show:

- Every finished video has a `qc_report.json` produced by **actually analysing the
  rendered file** (real frame brightness/variance, real silence detection, real
  loudness measurement) — not a self-report.
- Publishing is never marked successful without a real platform ID that AX re-reads
  back from the API.
- Revenue is tracked through `REPORTED → VERIFIED → BALANCE AVAILABLE → PAYOUT
  ELIGIBLE → CASH RECEIVED`, and currently stands at **฿0.00** because no
  monetisation channel is active.
- Every market number in `docs/MARKET_RESEARCH.md` is reproducible from the raw
  snapshots in `research/`.

## Pipeline

```
RESEARCH → SELECT → SCRIPT → STORYBOARD → ASSET GENERATION
        → VOICE/MUSIC → EDIT → QUALITY CONTROL → PACKAGE → PUBLISH → MEASURE
```

| Stage | Module | What it actually does |
|---|---|---|
| Research | `pipeline/research.py` | Pulls public YouTube metadata with yt-dlp, stores raw JSON |
| Analyse | `pipeline/analyze.py` | Extracts pattern tables from the snapshots |
| Script | `pipeline/gen_specs.py`, `content/specs/*.json` | Original writing, structured as scenes |
| Assets | `pipeline/video.py` | Draws every frame procedurally with PIL (gradients, glow, particles, captions) |
| Voice | `pipeline/tts.py` | edge-tts free neural voices |
| Music | `pipeline/audio.py` | Synthesises an original ambient bed with NumPy |
| Edit | `pipeline/video.py`, `pipeline/produce.py` | Encodes, concatenates, muxes, loudness-normalises |
| QC | `pipeline/produce.py::run_qc` | 16 real checks on the finished file |
| Package | `pipeline/produce.py` | `final.mp4`, `thumbnail.png`, `metadata.json`, `qc_report.json` |
| Publish | `pipeline/publisher.py` | YouTube Data API uploader + honest dry-run/BLOCKED modes |
| Measure | `pipeline/analytics.py` | Pulls real stats for verified publications only |

## Run it

```bash
# full loop
./run_loop.sh

# or piece by piece
python3 pipeline/research.py --queries "scary stories shorts" --limit 20
python3 pipeline/batch.py --workers 3
python3 pipeline/store.py sync
python3 pipeline/report.py
```

Output for each piece lands in `content/<slug>/`.

## Cost

฿0. Every component is free tier or open source, and the project will not
subscribe to anything, buy credits, or run ads without K's explicit approval.
See [`docs/TOOLS.md`](docs/TOOLS.md) for the verified tool inventory and the
reasoning behind the generative-visual decision.

## Documentation

- [`docs/STATUS.md`](docs/STATUS.md) — evidence-backed status, updated by every loop
- [`docs/MARKET_RESEARCH.md`](docs/MARKET_RESEARCH.md) — real data, patterns, niche choice
- [`docs/TOOLS.md`](docs/TOOLS.md) — what was tested and what was rejected
- [`docs/PUBLISHING.md`](docs/PUBLISHING.md) — the one action needed from K

## Rights and originality

All narrative text is original writing. All music is synthesised from scratch. All
visuals are drawn procedurally. Public platform metadata is used for research only;
no third-party footage, music, script or image is downloaded or republished. The
`provenance` block in every `metadata.json` states this explicitly and lists
third-party assets as empty.

## Licence

Code: MIT. Content produced by the pipeline: © the channel owner.
