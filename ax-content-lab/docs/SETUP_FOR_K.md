# SETUP FOR K — the only things AX cannot do alone

AX has built and verified everything else. Each item below is free and takes a
few minutes. Do them once; after that the system runs unattended.

Account to use for everything: **aerismusic8@gmail.com**

> **Looking for step-by-step links?** See `docs/K_ACTION_PLAN.md` — the same
> steps with every URL ready to click, plus verification commands and a
> troubleshooting table.

Status (verified 2026-10-19 from `python3 pipeline/connect.py check`):

| Item | State |
|---|---|
| GitHub write access (PERSIST) | **DONE** — `can_push: true`, login `aerismusic8-alt` |
| YouTube upload | BLOCKED — needs `secrets/youtube_token.json` |
| TikTok / Facebook / Instagram | BLOCKED — needs their tokens |

Remaining: **one credential per platform.** Only item 1 (YouTube) is needed to
start publishing; items 2–3 are optional extras.

---

## 0. GitHub write access — DONE (no action needed)

K's fine-grained PAT is installed at `secrets/github_pat.txt` (mode 600,
git-ignored). `connect.py check` reports `authenticated: true`, `can_push: true`
via a real write probe, and `bash pipeline/sync_repo.sh` pushes successfully.
Nothing to do here unless the token is later revoked.

*Optional:* the PAT lacks "Pull requests: write", so AX cannot open PRs. Add
that permission if you want PRs; the branch itself is public and readable.

---

## 1. YouTube upload authorisation (5 min) — unlocks publishing

**Problem AX hit:** uploading requires an OAuth token bound to your Google
account. No platform offers a legitimate anonymous upload path, and AX will not
use credential-evasion tools (project rule 5).

**Important:** `publisher.py` opens a local browser for consent, and this
sandbox has no browser. So use **Google's OAuth Playground** (from your own PC)
to mint the token, then hand it to AX. The full click-by-click walkthrough with
every URL is in **`docs/K_ACTION_PLAN.md`** and `docs/POST_ONE_CLIP.md`.

Short version:

1. https://console.cloud.google.com/projectcreate → project `ax-content-lab`
2. https://console.cloud.google.com/apis/library/youtube.googleapis.com →
   **Enable** YouTube Data API v3
3. https://console.cloud.google.com/apis/credentials/consent → **External**,
   app name `AX Content Lab`; under **Test users** add `aerismusic8@gmail.com`
4. https://console.cloud.google.com/apis/credentials → **Create credentials →
   OAuth client ID → Desktop app** → note the **Client ID** + **Client secret**
5. https://developers.google.com/oauthplayground/ → gear icon → tick **Use your
   own OAuth credentials** → paste the Client ID + secret → pick
   `https://www.googleapis.com/auth/youtube.upload` → **Authorize APIs** →
   **Exchange authorization code for tokens**
6. Give AX the resulting JSON (it must contain `access_token`, `refresh_token`,
   `client_id`, `client_secret`):
   ```bash
   python3 pipeline/connect.py youtube-token --token <path-to-json>
   ```
   AX verifies the token really carries `youtube.upload` against Google before
   saving `secrets/youtube_token.json` (mode 600, git-ignored).

Verify with `python3 pipeline/connect.py status` — `youtube_token` must be
`true` (and `ready_to_publish_youtube: true`). `connect.py check` only reports
`client_present`, so it is not the right probe for the token. **Cost: ฿0.**
Quota: 10,000 units/day ≈ **6 uploads/day**; the scheduler uses 4.

---

## 2. TikTok (10 min)

1. https://developers.tiktok.com/ → sign in as `aerismusic8@gmail.com`
2. **Manage apps → Connect an app** → add **Content Posting API**
3. Request scope **video.upload** (and `user.info.basic`)
4. Copy **Client key** + **Client secret** → paste at `/connect`
   (stored as `secrets/tiktok_client.json`)
5. One-time browser consent → `secrets/tiktok_token.json`

Uploads land in the creator inbox for you to confirm — that is TikTok's own
design. **Cost: ฿0.**

---

## 3. Facebook Page + Instagram (15 min, same Meta app)

1. Create a **Facebook Page** for the brand (free), signed in as
   `aerismusic8@gmail.com`
2. https://developers.facebook.com/ → **Create App** → type **Business**
3. Add products **Facebook Login** and **Instagram Graph API**
4. **Graph API Explorer** → request these permissions → **Generate Access Token**:
   `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`,
   `instagram_basic`, `instagram_content_publish`
5. **Extend Access Token** to a long-lived Page token
6. Convert Instagram to **Business/Creator** and link it to the Page
7. Get IDs: Page ID via `GET /me/accounts`; IG user ID via
   `GET /{page-id}?fields=instagram_business_account`
8. Write `secrets/meta_token.json`:
   ```json
   {"access_token": "EAAG...", "page_id": "1234567890", "ig_user_id": "1789..."}
   ```

Instagram Reels needs the video at a public URL; set `AX_PUBLIC_BASE` to the
public gallery address so IG can pull it. Facebook Reels works either way.
**Cost: ฿0.**

---

## 4. Create the channel identity (3 min)

Channel creation is tied to a Google account and cannot be delegated to AX.

1. https://www.youtube.com → sign in as `aerismusic8@gmail.com`
2. Create a channel named **AX Viral Content Lab**
3. Upload the ready-made branding from `brand/`:
   - `brand/avatar.png` (800×800) → profile picture
   - `brand/banner.png` (2560×1440) → banner (safe area is the centre strip)
   - `brand/endcard.png` → pinned/end card

---

## 5. Google Drive backup — CONNECTED

K authorised Drive once (`rclone authorize "drive"`); the token is stored in
git-ignored `secrets/drive_token.json`, so it survives sandbox resets and AX
rebuilds the rclone remote automatically. Verified: `drive_sync.py --status`
reports `ready: true` and a real upload completed.

```
python3 pipeline/drive_sync.py --snapshot   # dated folder of all AI-art videos
python3 pipeline/drive_sync.py --upload      # content/, docs/, brand/
python3 pipeline/drive_sync.py --status      # what is connected
```

Snapshots land in **AX Content Lab / AI_Art_Batch_<date>** on Drive (account
aerismusic8@gmail.com), each with `README.md` + `MANIFEST.json` and sha256 per
video. **Cost: ฿0.**

Note: rclone warns its shared Google client_id retires during 2026. If it stops
working, make a free client_id (rclone.org/drive) and re-authorise.

---

## What AX does after each step

- Re-reads the credential files and reports exactly what is ready and what is
  still blocked — never a guessed status (`python3 pipeline/multipost.py --status`).
- Runs the consent flow for anything needing a browser.
- Starts the scheduled poster: **09:00, 13:00, 18:00, 21:00 (UTC+7)**, one item
  per platform per slot, skipping anything already posted.
- Records a post as `PUBLISHED` only when the platform returns a real id/url.
- Pulls real view/like/comment numbers afterwards. Revenue stays ฿0.00 until a
  payout is actually received.

## Honest limits

- No platform allows anonymous upload. AX cannot work around this.
- Monetization (YouTube Partner Program) needs 1,000 subscribers and 10M Shorts
  views in 90 days, plus an approved AdSense account in your name. AX cannot open
  AdSense for you — that step is yours once the numbers are reached.

---

## What AX already did so K does not have to

- Built the whole pipeline and verified it (40 videos produced, 40/40 QC PASS).
- Generated all channel branding (`brand/`).
- Wrote the YouTube, TikTok, Facebook and Instagram uploaders, the analytics
  puller, and the time-based scheduler.
- Wrote this list so K's total effort is ~30 minutes, not days.

