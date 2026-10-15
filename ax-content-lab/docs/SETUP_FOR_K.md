# SETUP FOR K — the only things AX cannot do alone

AX has built and verified everything else. Each item below is free and takes a
few minutes. Do them once; after that the system runs unattended.

Account to use for everything: **aerismusic8@gmail.com**

Status: **GitHub is connected** (write verified). Remaining: the four channels.

---

## 0. GitHub write access — DONE

The fine-grained PAT is installed and verified (`can_push: true`). Code and
evidence push automatically via `bash pipeline/sync_repo.sh`. Nothing to do here.

---

## 1. YouTube upload authorisation (5 min) — unlocks publishing

**Problem AX hit:** uploading requires an OAuth token bound to your Google
account. No platform offers a legitimate anonymous upload path, and AX will not
use credential-evasion tools (project rule 5).

**Fix:**

1. https://console.cloud.google.com/ → create a project (free), name it
   `ax-content-lab`
2. **APIs & Services → Library** → search **YouTube Data API v3** → **Enable**
3. **APIs & Services → OAuth consent screen** → **External** → app name
   `AX Content Lab`, your email → Save. Under **Test users**, add
   `aerismusic8@gmail.com`
4. **APIs & Services → Credentials → Create credentials → OAuth client ID**
   → Application type **Desktop app** → Create → **Download JSON**
5. Paste the JSON at
   https://work-1-vrswmageirdabiwu.prod-runtime.all-hands.dev/connect
   (or drop it in `secrets/youtube_client_secret.json`)

A browser opens once for consent (cached afterwards). **Cost: ฿0.**
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

- Built the whole pipeline and verified it (30 videos targeted, all QC PASS).
- Generated all channel branding (`brand/`).
- Wrote the YouTube, TikTok, Facebook and Instagram uploaders, the analytics
  puller, and the time-based scheduler.
- Wrote this list so K's total effort is ~30 minutes, not days.

