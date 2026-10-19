# Publishing — What AX can do alone, and what needs K

Verified 2026-10-14. AX does **not** claim any post succeeded unless the platform
returns a real video ID / URL that AX can re-read.

## Status of each channel

| Platform | Automated upload possible? | Why | What K must do |
|---|---|---|---|
| YouTube (Data API v3) | Yes — code is ready in `pipeline/publisher.py` | Requires an OAuth 2.0 client owned by the account holder | Create a Google Cloud project + OAuth client, download the JSON (5 min, free) |
| TikTok (Content Posting API) | Yes, after app review | Requires a registered app and a user access token | Register app at developers.tiktok.com, complete audit |
| Instagram / Facebook (Meta Graph API) | Yes, for Business/Creator accounts | Requires a Meta app + a linked IG Business account + page token | Create Meta app, link IG Business account |
| X / Threads / others | Partial | Varies; most need developer app approval | Register developer app |

**No platform offers a legitimate anonymous upload path.** Any tool that claims
otherwise is either using stolen credentials or violating the platform terms, so
AX will not use one (project rule 5).

## YouTube — the one concrete action AX needs from K

AX has already written and tested the uploader. It cannot run without an OAuth
client secret that only the account holder can create.

1. Go to https://console.cloud.google.com/ and create a project (free).
2. **APIs & Services → Library →** enable **YouTube Data API v3**.
3. **APIs & Services → OAuth consent screen** → External → fill the app name
   and your email → add your own Google account under **Test users**.
4. **APIs & Services → Credentials → Create credentials → OAuth client ID**
   → Application type: **Desktop app** → Create → **Download JSON**.
5. Save the downloaded file to this exact path:

   ```
   secrets/youtube_client_secret.json
   ```

6. Mint the token with **Google OAuth Playground** (this sandbox has no browser,
   and `publisher.py` opens one via `flow.run_local_server`). Full click-by-click
   steps live in **`docs/K_ACTION_PLAN.md` §1** — do not duplicate them here.
   Then hand AX the token JSON:

   ```bash
   python3 pipeline/connect.py youtube-token --token <path-to-json>
   ```

   AX verifies the `youtube.upload` scope against Google before saving
   `secrets/youtube_token.json`. Verify with `connect.py status`
   (`youtube_token: true`), then upload:

   ```bash
   python3 pipeline/publisher.py --slug 0001_the_last_signal --privacy private
   ```

> **Canonical setup doc:** `docs/K_ACTION_PLAN.md` is the single source of truth
> for credential steps (URLs + verification). `docs/SETUP_FOR_K.md` is the short
> summary; `docs/POST_ONE_CLIP.md` is the fastest path for one test clip. If they
> ever disagree, `K_ACTION_PLAN.md` wins.

---

**Cost: ฿0.** The YouTube Data API upload quota (10,000 units/day) allows roughly
6 uploads/day, which matches the production target.

> `secrets/` is git-ignored. Never commit the client secret or the token.

## Recommended safe rollout

1. Upload the first video as **private** and confirm it plays.
2. If the channel is new, YouTube may hold uploads for verification.
   Custom thumbnails require a verified channel.
3. Move to **unlisted** → **public** once the channel looks healthy.
4. Keep uploads to ≤6/day so the API quota is never exhausted.

## Channel creation

Channel creation also requires the account holder's Google account. AX cannot
create a channel without that identity. Once K creates the channel, AX can set
the branding assets (it already generates `thumbnail.png` and can generate
banners/logos with the same renderer).

## What AX has verified it *can* do without K

- Research public market data (yt-dlp) — verified.
- Write original scripts and generate original visuals, music and narration — verified.
- Render, encode and quality-check publish-ready video files — verified (30/30 PASS).
- Validate that every package is complete and QC-passed — verified.
- Upload automatically the moment an OAuth token exists — code written, tested up
  to the auth boundary; will be verified end-to-end once K provides the client secret.
