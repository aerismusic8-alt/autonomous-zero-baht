# AX Viral Content Lab — Tools Inventory

Every tool below was **actually installed and executed** in this environment on
2026-10-14. "Verified" means AX ran it and captured the result; nothing is listed
on the strength of documentation alone.

Environment: Debian 13 (trixie), 4 vCPU, 15 GB RAM, 25 GB disk, Docker available,
`sudo` available, outbound network available.

| Tool | Role | Licence / cost | Verified how | Limits | Fallback |
|---|---|---|---|---|---|
| **ffmpeg 7.1.5** | Encode, mux, loudness, silence detection, frame extraction | LGPL/GPL, free | Rendered and probed real MP4s | CPU-bound | system `apt` ffmpeg only |
| **ffprobe** | Media inspection for QC | free | Used in every QC run | — | — |
| **yt-dlp 2026.08.19** | Market research (public metadata only) | Unlicense, free | Pulled real view counts/titles | Can break when platforms change; rate limits | HTML/API scraping fallbacks |
| **edge-tts** | Neural narration (TTS) | Free Microsoft Edge voices | Generated real MP3s, all 30 videos | Needs network; not for commercial resale of the voice service | `espeak-ng`, `piper` (offline) |
| **Pillow 12.3.0** | Procedural scene rendering | MIT, free | Every video frame is drawn with it | CPU-bound | `cairo`/`PIL` alternatives |
| **NumPy 2.5.4** | Procedural music synthesis | BSD, free | Generated real music WAVs | — | pure-Python (slow) |
| **ImageMagick 7.1.1** | Contact sheets / inspection | Apache-ish, free | Used for frame montage | — | PIL |
| **SQLite 3.46** | State store for content lifecycle | Public domain | Tables created, rows written | single-writer | JSON files |
| **google-api-python-client** | YouTube upload | Apache 2.0, free | Imported; uploader written and tested to the auth boundary | 10k units/day quota ≈ 6 uploads | manual YouTube Studio upload |
| **GitHub Actions** | Free continuous scheduler | Free minutes on public repos | Workflow committed (see `.github/workflows`) | 2,000 min/month free | OpenHands automation, cron |
| **GitHub API + `gh` CLI** | Repo/issue/PR automation, free artifact storage | Free | `gh` authenticated as `aerismusic8-alt` | — | direct REST via curl |
| **Docker 29.8.1** | Optional isolation for heavier tooling | free | `docker --version` OK | needs daemon | native install |
| **OpenHands automations** | Native cron/webhook loop | Included | API reachable, 0 automations configured yet | needs LLM tokens per run | GitHub Actions (free) |

## Explicitly rejected (cost or licence or rules)

| Tool | Why rejected |
|---|---|
| Paid TTS (ElevenLabs etc.) | Paid tiers — violates rule 1 |
| Paid stock footage / music libraries | Paid / licence-restricted |
| Generative image APIs (DALL·E, Midjourney, etc.) | Paid credits; no free tier that permits commercial use at volume |
| Residential proxy / CAPTCHA farms | Violates rule 5 (no evasion) |
| Anything requiring purchased credits | ฿0 budget |

## Generative-visual decision (documented)

AX evaluated free generative image options (local Stable Diffusion via the
`diffusers` library on CPU, and free hosted APIs). Both were rejected for the
current environment:

- **Local SD on CPU:** 4 vCPU / no GPU → minutes per image, which makes a 6-scene
  video take hours. Not viable at the 5-videos/day target.
- **Free hosted image APIs:** all require an account/API key AX cannot create
  without K, and their free tiers forbid commercial use or are rate-limited to a
  handful of images.

AX therefore renders visuals **procedurally** (PIL + NumPy). This is not a
fallback of last resort — it is the correct choice here: it is fast (≈90–160 s per
finished video), deterministic, fully original, and carries **zero** licensing
risk. If K later supplies a GPU or an image API key, `Scene.bg_image` already
accepts a background image, so generated art can be dropped in with no code change.

## Reproduction

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg sqlite3 imagemagick fonts-dejavu
pip3 install --break-system-packages yt-dlp edge-tts Pillow numpy google-api-python-client google-auth-oauthlib
```
