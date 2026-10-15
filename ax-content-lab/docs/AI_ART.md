# Visual style: AI-illustrated scenes

## Why this exists

The first build rendered a **gradient plus captions** - no characters, no scenes,
no illustrated imagery. Measured on a real frame: ~10,900 unique colours. The
reference channels this niche competes with (e.g. "20 True Creepy Horror Stories
Animated", 2.99M views) are **2D animated character stories**. The gap was the
visuals, not the script.

This layer adds real illustrations under each scene, so a shot now shows a place
and a subject, and the frame moves.

## What changed

| Layer | Before | Now |
|---|---|---|
| Scene image | flat gradient + particles | AI illustration (anime / 3D / painterly) |
| Motion | drifting glow only | slow Ken Burns push-in + pan over the art |
| Captions | caption text | unchanged (still bottom-third, readable) |
| Thumbnail | gradient + text | hero AI illustration + text |
| QC | 16 checks | 18 checks (adds AI-art provenance + licence flag) |
| Measured colours/frame | ~10,900 | ~39,000-55,000 |

## How it works

`pipeline/aiart.py` calls **Pollinations.ai** (`image.pollinations.ai`):

- open-source platform (MIT), public endpoint, **no signup, no API key, no cost**
- returns a JPEG; the free endpoint resolves to ~576x1024, which we upscale to
  1080x1920 with Lanczos and then Ken-Burns crop (the upscale is acceptable at
  short-form bitrates; it is not a native 1080p render)
- **rate-limited per IP** (~40 s/image). Parallel workers do not help. The cache
  keyed by prompt+seed+model makes a re-run resume instantly, so a full 30-video
  pass is a one-time ~2 h job, then cached.

`pipeline/art_prompts.py` gives each series a pool of six original visual beats
(establishing shot -> tension -> detail -> reveal -> aftermath -> final frame) and
assigns one per scene, with a **per-slug, per-scene seed** so two stories in the
same series never render the same picture.

`pipeline/produce.py --art` wires it in: generate art per scene, render with Ken
Burns, use the hero image as the thumbnail, and record provenance.

## Provenance and licence

Every generated asset writes a sidecar JSON and is recorded in
`content/<slug>/metadata.json` under `provenance.ai_art`:

- the exact prompt, style anchor, seed, model, provider
- `sha256` of the bytes, so a frame is reproducible and auditable
- a `license_note`

**Licence caveat (read before monetising):** the Pollinations platform code is MIT
and the public endpoint is free, but the hosted endpoint routes to whichever free
model is available and **individual model licences vary**. These outputs are
therefore treated as "provider-returned art for review". The seed and prompt are
kept for every asset so any image can be regenerated or dropped. Do not push
AI-art videos to a monetised channel until K confirms the model licence, or
regenerate on a known-licence model. QC raises `ai_art_license_flagged` on every
AI-art video for exactly this reason.

## Quality control for art

Two checks were added, only when art is used:

- `ai_art_provenance` - every asset has a seed, a sha256 and a licence note
- `ai_art_license_flagged` - always present, so the caveat cannot be missed

## Reproduce

```bash
python3 pipeline/art_prompts.py                      # attach prompts + seeds
python3 pipeline/produce.py content/specs/spec_0001_the_last_signal.json --art --force
python3 pipeline/batch.py --workers 1 --art          # all specs (sequential; IP limited)
```
