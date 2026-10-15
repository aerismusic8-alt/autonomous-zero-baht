# Post ONE clip to YouTube / Facebook Reels / TikTok — K's 10 minutes

Everything is built and dry-run-verified. The uploaders only need credentials;
each platform ties an upload to a real account, so only K can grant them.

Test clip: **0001_the_last_signal** (Deep Space Logs, 23.5s, 1080×1920, QC 18/18).

Preview exactly what will be posted, no credentials needed:

```
python3 pipeline/multipost.py --dry-run --platform youtube --slug 0001_the_last_signal
python3 pipeline/multipost.py --status      # what is ready, what is missing
```

---

## 1. YouTube Shorts (5 min) — OAuth Playground, no browser in the sandbox

The sandbox has no browser, so use Google's own OAuth Playground from your PC.

1. https://console.cloud.google.com/ → new project `ax-content-lab` (free)
2. **APIs & Services → Library** → enable **YouTube Data API v3**
3. **Credentials → Create credentials → OAuth client ID → Desktop app** → Create
   → copy the **Client ID** and **Client secret** (keep this tab open)
4. https://developers.google.com/oauthplayground/ → gear icon (top right):
   - tick **Use your own OAuth credentials** → paste the Client ID + secret
5. In the left list pick **YouTube Data API v3** →
   `https://www.googleapis.com/auth/youtube.upload` → **Authorize APIs**
6. Sign in as **aerismusic8@gmail.com** → allow → **Exchange authorization code
   for tokens** (this yields an access token *and* a refresh token)
7. Copy the JSON shown (it includes `access_token`, `refresh_token`, `client_id`,
   `client_secret`) and hand it to AX. Either:
   - paste it at the `/connect` page, **or**
   - save it as `secrets/yt_playground.json` and run:

```
python3 pipeline/connect.py youtube-token --token secrets/yt_playground.json
```

AX verifies the token really carries `youtube.upload` before saving
(`secrets/youtube_token.json`, mode 600, git-ignored). Then:

```
python3 pipeline/multipost.py --platform youtube --slug 0001_the_last_signal --privacy private
```

Post it **private** first, watch it, then re-run with `--privacy public`.
Quota: 10,000 units/day ≈ 6 uploads/day. Cost ฿0.

---

## 2. Facebook Reels (5 min)

1. Create a **Facebook Page** for the brand, signed in as aerismusic8@gmail.com
2. https://developers.facebook.com/ → **Create App** → type **Business**
3. Add product **Facebook Login**; in **Graph API Explorer** request
   `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`
4. **Extend Access Token**, then get the **Page token** and **Page ID**
   (`GET /me/accounts`)
5. Save `secrets/meta_token.json`:

```json
{"access_token": "<page token>", "page_id": "<page id>", "ig_user_id": ""}
```

```
python3 pipeline/multipost.py --platform facebook --slug 0001_the_last_signal
```

---

## 3. TikTok (10 min)

1. https://developers.tiktok.com/ → sign in as aerismusic8@gmail.com
2. **Manage apps → Connect an app** → add **Content Posting API**,
   scope **video.upload** (+ `user.info.basic`)
3. Save `secrets/tiktok_client.json`:

```json
{"client_key": "...", "client_secret": "..."}
```

4. One-time browser consent → save the returned token as
   `secrets/tiktok_token.json`:

```json
{"access_token": "...", "refresh_token": "...", "open_id": "..."}
```

```
python3 pipeline/multipost.py --platform tiktok --slug 0001_the_last_signal
```

TikTok delivers uploads to the creator inbox for you to confirm — that is
TikTok's own design, not a failure.

---

## 4. Instagram Reels (reuses the Meta token, 2 min)

Link an Instagram **Business/Creator** account to the same Page, put its
`ig_user_id` in `secrets/meta_token.json`, set a public base URL, then:

```
export AX_PUBLIC_BASE=https://<your-public-host>
python3 pipeline/multipost.py --platform instagram --slug 0001_the_last_signal
```

Instagram pulls the video from a public URL, so `AX_PUBLIC_BASE` must point at
a host serving `content/<slug>/final.mp4`.

---

## Honest status

A post is recorded **PUBLISHED** only when the platform returns a real id/url,
which AX stores. Until a credential above exists, `--status` says `ready: false`
and nothing is claimed as posted. No platform allows an anonymous upload, and AX
will not use credential-evasion tools.
