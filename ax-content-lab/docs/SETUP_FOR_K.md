# SETUP FOR K — the only 3 things AX cannot do alone

AX has built and verified everything else. Each item below is free and takes a
few minutes. Do them once; after that the system runs unattended.

Account to use for everything: **aerismusic8@gmail.com**

---

## 1. GitHub write access (2 min) — unlocks saving all code + evidence

**Problem AX hit:** the GitHub token in the environment is authenticated as
`aerismusic8-alt` but has **no scopes** (`x-oauth-scopes:` is empty), so every
write is rejected with `403 Resource not accessible by integration`. AX can read
repos and has `ADMIN` as *viewer*, but the token itself cannot push.

**Fix — create a fine-grained Personal Access Token:**

1. Go to https://github.com/settings/personal-access-tokens/new (signed in as `aerismusic8-alt`)
2. Token name: `ax-content-lab`
3. Expiration: 90 days (or custom)
4. Repository access: **Only select repositories** → `autonomous-zero-baht`
   (or all repositories)
5. Permissions → Repository permissions:
   - **Contents: Read and write** ← required
   - **Workflows: Read and write** ← required (the loop workflow)
   - **Metadata: Read-only** (auto)
6. Generate, copy the token (starts with `github_pat_...`)

**Then run exactly this:**

```bash
python3 pipeline/connect.py github --token github_pat_XXXXXXXX
python3 pipeline/connect.py check
```

Expected result: `"can_push": true`. AX will then push everything automatically.

> AX will never print or commit the token. It is stored at `secrets/github_pat.txt`
> (chmod 600) and `secrets/` is git-ignored.

---

## 2. YouTube upload authorisation (5 min) — unlocks publishing

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
5. Install it and upload the first video as **private**:

```bash
python3 pipeline/connect.py youtube --client ~/Downloads/client_secret_XXXX.json
python3 pipeline/publisher.py --slug 0001_the_last_signal --privacy private
```

A browser opens once for consent (cached afterwards). **Cost: ฿0.**

---

## 3. Create the channel (3 min) — the identity step

Channel creation is tied to a Google account and cannot be delegated to AX.

1. https://www.youtube.com → sign in as `aerismusic8@gmail.com`
2. Create a channel named **AX Viral Content Lab**
3. Upload the ready-made branding from `brand/`:
   - `brand/avatar.png` (800×800) → profile picture
   - `brand/banner.png` (2560×1440) → banner (safe area is the centre strip)
   - `brand/endcard.png` → can be used as a pinned/end card
4. Tell AX the channel URL, and AX takes over the rest.

---

## Optional — other platforms

Same pattern. Provide a token and AX stores it in
`secrets/platform_tokens.json` and extends the publisher:

| Platform | Where to register | Token type |
|---|---|---|
| TikTok | https://developers.tiktok.com (Content Posting API) | user access token after app audit |
| Instagram / Facebook | https://developers.facebook.com (Graph API) | page/IG access token, needs IG Business account |
| X | https://developer.x.com | OAuth 2.0 user token |

AX has written the YouTube uploader end to end. The others follow the same shape
and can be added in about an hour each once tokens exist.

---

## What AX already did so K does not have to

- Built the whole pipeline and verified it (10 videos, 10/10 QC PASS).
- Generated all channel branding (`brand/`).
- Wrote the uploader, analytics and scheduler.
- Wrote this list so K's total effort is ~10 minutes, not days.
