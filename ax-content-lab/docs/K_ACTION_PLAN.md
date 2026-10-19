# K ACTION PLAN — ลิงก์และขั้นตอนละเอียด

> เอกสารนี้คือแผนลงมือทำสำหรับ K (เจ้าของบัญชี) ทุกอย่าง **ฟรี ฿0**
> ทุกคำสั่งตรวจสอบได้จริงจากไฟล์หรือ API response ไม่มีการเดาสถานะ
>
> บัญชีที่ใช้ทุกอย่าง: **aerismusic8@gmail.com**
> Repo: https://github.com/aerismusic8-alt/autonomous-zero-baht
> Branch: `ax-content-lab`

## ลิงก์ตรงทั้งหมด (คัดลอกไปเปิดได้เลย)

| ต้องทำ | ลิงก์ |
|---|---|
| 0. สร้าง GitHub PAT | https://github.com/settings/personal-access-tokens/new |
| 1. สร้างโปรเจกต์ Google Cloud | https://console.cloud.google.com/projectcreate |
| 1. เปิด YouTube Data API v3 | https://console.cloud.google.com/apis/library/youtube.googleapis.com |
| 1. OAuth consent screen | https://console.cloud.google.com/apis/credentials/consent |
| 1. สร้าง OAuth client ID | https://console.cloud.google.com/apis/credentials |
| 2. TikTok developer apps | https://developers.tiktok.com/apps/ |
| 3. สร้าง Meta app | https://developers.facebook.com/apps/ |
| 3. Graph API Explorer | https://developers.facebook.com/tools/explorer/ |
| 3. ขยายอายุ Meta token | https://developers.facebook.com/tools/debug/accesstoken/ |
| 4. สร้างช่อง YouTube | https://www.youtube.com |
| Repo (อ่านอย่างเดียว) | https://github.com/aerismusic8-alt/autonomous-zero-baht/tree/ax-content-lab |

> ทุก provider link ตรวจแล้วตอบ HTTP 200/302 (ใช้งานได้) ณ 2026-10-19

---

## สถานะปัจจุบัน (ยืนยันจาก `connect.py check`)

| รายการ | สถานะ | ไฟล์ที่ต้องมี |
|---|---|---|
| GitHub push (PERSIST) | 🟢 DONE | `secrets/github_pat.txt` (can_push: true) |
| YouTube upload | 🔴 BLOCKED | `secrets/youtube_token.json` |
| TikTok | 🔴 BLOCKED | `secrets/tiktok_client.json` + `tiktok_token.json` |
| Facebook / Instagram | 🔴 BLOCKED | `secrets/meta_token.json` |
| Google Drive backup | 🟢 CONNECTED | `secrets/drive_token.json` |

งานที่ AX ทำเสร็จแล้ว: 40 วิดีโอ, QC PASS 40/40, รอ publish อย่างเดียว
(ยังไม่เผยแพร่แม้แต่ชิ้นเดียว — ไม่มี platform ID, รายได้ ฿0.00)

---

## ลำดับความสำคัญ

ทำ **ข้อ 0** ก่อน (ใช้เวลา 3 นาที) เพราะปลดล็อกการ push งานทั้งหมดขึ้น GitHub
จากนั้นทำ **ข้อ 1** เพื่อเริ่ม publish ได้

---

## 0. GitHub PAT — ปลดล็อก PERSIST (3 นาที) ⚠️ ทำก่อน

**ปัญหา:** `sync_repo.sh` push ไม่ได้ — token เดิมคืน `401 Bad credentials`
และ push คืน `403` งานทั้ง 40 ชิ้น commit ไว้ในเครื่องแต่ยังไม่ขึ้น repo

### ขั้นตอน

1. เปิดลิงก์สร้าง token (fine-grained):
   **https://github.com/settings/personal-access-tokens/new**

2. กรอก:
   - **Token name:** `ax-content-lab-write`
   - **Expiration:** 90 days (หรือตามต้องการ)
   - **Repository access:** เลือก **Only select repositories**
     → เลือก **`aerismusic8-alt/autonomous-zero-baht`**
   - **Permissions → Repository permissions:**
     - **Contents: Read and write** ← จำเป็นที่สุด
     - **Metadata: Read-only** (จะถูกเลือกอัตโนมัติ)
     - (ถ้าต้องการให้เปิด PR ได้ในอนาคต) **Pull requests: Read and write**

3. กด **Generate token** → **คัดลอกทันที** (ขึ้นต้นด้วย `github_pat_`
   จะเห็นครั้งเดียว)

4. ส่ง token ให้ AX — เลือกวิธีใดวิธีหนึ่ง:
   - **วิธี B (ผ่าน command line, ไม่ต้องพึ่ง server):**
     ```bash
     python3 pipeline/connect.py github --token github_pat_XXXX
     ```
   - **วิธี A (วางที่หน้า `/connect`):** หน้า intake เปิดได้เฉพาะตอน AX รัน
     `python3 pipeline/serve.py` อยู่ — AX จะพิมพ์ URL จริงออกมาเป็นบรรทัด
     `[serve] intake : <URL>/connect` ให้ใช้ URL นั้นตรง ๆ
     (hostname ของ runtime เปลี่ยนทุกเซสชัน อย่าใช้ URL ที่ค้างในเอกสารเก่า)

5. **ตรวจสอบว่าปลดล็อกจริง:**
   ```bash
   python3 pipeline/connect.py check
   ```
   ต้องเห็น `"can_push": true` ← ถ้าเห็นค่านี้แปลว่าเขียนได้จริง
   (fine-grained PAT จะไม่รายงาน `x-oauth-scopes` เป็นเรื่องปกติ ให้เชื่อ probe)

6. เมื่อผ่านแล้ว AX จะรัน `bash pipeline/sync_repo.sh` เพื่อ push
   งาน 40 ชิ้น + 5 spec ใหม่ขึ้น repo ได้

---

## 1. YouTube — ปลดล็อก PUBLISH (5 นาที)

**ปัญหา:** upload ต้องมี OAuth token ที่ผูกกับบัญชี Google ของ K
ไม่มีแพลตฟอร์มไหนให้อัปโหลดแบบไม่ระบุตัวตน และ AX จะไม่ใช้เครื่องมือหลบเลี่ยง

### ขั้นตอน (มีลิงก์ตรงทุกขั้น)

1. **สร้างโปรเจกต์** (ฟรี):
   **https://console.cloud.google.com/projectcreate**
   ตั้งชื่อ `ax-content-lab` → Create

2. **เปิดใช้ YouTube Data API v3:**
   **https://console.cloud.google.com/apis/library/youtube.googleapis.com**
   → เลือกโปรเจกต์ `ax-content-lab` → กด **Enable**

3. **ตั้งค่า OAuth consent screen:**
   **https://console.cloud.google.com/apis/credentials/consent**
   - User type: **External** → Create
   - App name: `AX Content Lab`
   - User support email: `aerismusic8@gmail.com`
   - Developer contact email: `aerismusic8@gmail.com`
   - Save and continue ผ่าน Scopes (ไม่ต้องเพิ่ม) และ Test users
   - **Test users:** เพิ่ม `aerismusic8@gmail.com` ← จำเป็น
     (แอปอยู่ในโหมด Testing จะใช้ได้เฉพาะ test user)

4. **สร้าง OAuth client:**
   **https://console.cloud.google.com/apis/credentials**
   → **Create credentials → OAuth client ID**
   → Application type: **Desktop app**
   → Name: `AX Content Lab Desktop` → Create
   → จด **Client ID** และ **Client secret** ไว้

5. **ขอ token ผ่าน OAuth Playground** (sandbox ไม่มี browser จึงใช้วิธีนี้):
   **https://developers.google.com/oauthplayground/**
   - กดไอคอน ⚙️ มุมขวาบน → ติ๊ก **Use your own OAuth credentials**
     → ใส่ Client ID + Client secret จากข้อ 4
   - ช่องซ้าย เลือก **YouTube Data API v3** →
     `https://www.googleapis.com/auth/youtube.upload` → **Authorize APIs**
   - ล็อกอิน `aerismusic8@gmail.com` → เจอหน้า "Google hasn't verified this app"
     → **Advanced → Go to AX Content Lab (unsafe)** (ปลอดภัย เป็นแอปของ K เอง)
   - กด **Exchange authorization code for tokens**
   - ก๊อป JSON ทั้งก้อน (ต้องมี `access_token`, `refresh_token`, `client_id`,
     `client_secret`) → เก็บเป็นไฟล์

6. **ส่ง token ให้ AX:**
   ```bash
   python3 pipeline/connect.py youtube-token --token <path-to-json>
   ```
   AX จะยิง `tokeninfo` ตรวจกับ Google จริงว่า token มี scope `youtube.upload`
   ก่อนบันทึกเป็น `secrets/youtube_token.json` (mode 600, git-ignored)

7. **ตรวจสอบ:**
   ```bash
   python3 pipeline/connect.py status   # ต้องเห็น "youtube_token": true
   python3 pipeline/multipost.py --status
   ```
   (`connect.py check` รายงานแค่ `client_present` — ไม่ใช่ตัวตรวจ token)

**หมายเหตุ:** `publisher.py` ใช้ `flow.run_local_server()` ซึ่งต้องมี browser
บนเครื่องที่รัน — sandbox นี้ไม่มี จึงต้องใช้ Playground (ข้อ 5) แทน
ถ้า K รัน AX บนเครื่องตัวเองที่มี browser ใช้ `connect.py youtube --client <json>`
แล้วรัน `publisher.py --all --privacy private` ได้เลย

**โควตา:** 10,000 units/วัน ≈ **6 uploads/วัน** (scheduler ใช้ 4)
**ค่าใช้จ่าย: ฿0**

---

## 2. TikTok (10 นาที)

1. **https://developers.tiktok.com/** → ล็อกอินด้วย `aerismusic8@gmail.com`
2. **Manage apps → Connect an app** → เพิ่มผลิตภัณฑ์ **Content Posting API**
   (ลิงก์: https://developers.tiktok.com/apps/)
3. ขอ scope **`video.upload`** และ **`user.info.basic`**
4. คัดลอก **Client key** + **Client secret** → วางที่หน้า `/connect` ช่อง TikTok
   (เขียนลง `secrets/tiktok_client.json`)
   หรือ: `python3 pipeline/connect.py tiktok --client '{"client_key":"...","client_secret":"..."}'`
5. ขอ authorization URL:
   ```bash
   python3 pipeline/connect.py tiktok-url
   ```
   เปิดลิงก์ที่ได้ → กด Authorize → คัดลอก `code` จาก callback URL
6. ส่ง code กลับ:
   ```bash
   python3 pipeline/connect.py tiktok-code --code <CODE>
   ```
   → เขียนลง `secrets/tiktok_token.json`

**หมายเหตุ:** คลิปจะไปอยู่ใน creator inbox ให้ K กดยืนยันก่อนโพสต์
(เป็นดีไซน์ของ TikTok เอง) **ค่าใช้จ่าย: ฿0**

---

## 3. Facebook Page + Instagram (15 นาที, ใช้ Meta app เดียวกัน)

1. **สร้าง Facebook Page** สำหรับแบรนด์ (ฟรี) ด้วยบัญชี `aerismusic8@gmail.com`
2. **สร้างแอป:** https://developers.facebook.com/apps/
   → **Create App** → type **Business**
3. เพิ่มผลิตภัณฑ์: **Facebook Login** และ **Instagram Graph API**
4. **Graph API Explorer:** https://developers.facebook.com/tools/explorer/
   → เลือกแอป → เพิ่ม permissions เหล่านี้ → **Generate Access Token**:
   ```
   pages_show_list
   pages_read_engagement
   pages_manage_posts
   instagram_basic
   instagram_content_publish
   ```
5. **ขยายอายุ token:** https://developers.facebook.com/tools/debug/accesstoken/
   → วาง token → **Extend Access Token** (ได้ long-lived Page token)
6. **เตรียม Instagram:** เปลี่ยนเป็นบัญชี **Business/Creator** และผูกกับ Page
7. **หา IDs:**
   - Page ID: `GET /me/accounts`
   - IG user ID: `GET /{page-id}?fields=instagram_business_account`
8. **เขียนไฟล์** `secrets/meta_token.json`:
   ```json
   {
     "access_token": "EAAG...",
     "page_id": "1234567890",
     "ig_user_id": "1789..."
   }
   ```
   หรือวางที่หน้า `/connect` ช่อง Meta → Save

**Instagram Reels** ต้องให้วิดีโออยู่บน public URL → ตั้งค่า `AX_PUBLIC_BASE`
เป็นที่อยู่ public gallery เพื่อให้ IG ดึงไปได้
(ถ้าไม่ตั้ง จะคืน `BLOCKED: set AX_PUBLIC_BASE to a public URL`)
Facebook Reels ใช้ได้ทั้งสองทาง **ค่าใช้จ่าย: ฿0**

---

## 4. สร้างช่อง YouTube (3 นาที)

การสร้างช่องผูกกับบัญชี Google มอบให้ AX ทำแทนไม่ได้

1. **https://www.youtube.com** → ล็อกอิน `aerismusic8@gmail.com`
2. สร้างช่องชื่อ **AX Viral Content Lab**
3. อัปโหลดแบรนด์ที่เตรียมไว้แล้วจากโฟลเดอร์ `brand/`:
   - `brand/avatar.png` (800×800) → รูปโปรไฟล์
   - `brand/banner.png` (2560×1440) → แบนเนอร์ (safe area = แถบกลาง)
   - `brand/endcard.png` → pinned / end card

---

## ตรวจสอบหลังทำทุกข้อ

```bash
python3 pipeline/connect.py check          # can_push, youtube.client_present
python3 pipeline/multipost.py --status     # per-platform ready: true/false
python3 pipeline/publisher.py --all --privacy private   # อัปโหลดจริง
python3 pipeline/analytics.py              # ดึงสถิติจริงหลังมี publication
bash pipeline/sync_repo.sh                 # push ขึ้น GitHub
```

หลักการบันทึกสถานะ: publication จะถูกบันทึกเป็น `PUBLISHED`
**เฉพาะเมื่อแพลตฟอร์มคืน id/url จริง** เท่านั้น ถ้าไม่คืน = `BLOCKED`
รายได้คงเป็น ฿0.00 จนกว่าจะได้รับเงินจริง (`CASH RECEIVED`)

---

## แก้ปัญหาเบื้องต้น

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `check` คืน `can_push: false` | PAT ไม่มี Contents: write | สร้าง PAT ใหม่ให้สิทธิ์ Contents: Read and write |
| `sync_repo.sh` exit 2 | ไม่พบ `secrets/github_pat.txt` | รันข้อ 0 |
| `sync_repo.sh` exit 4 | push ถูกปฏิเสธ (สิทธิ์ไม่พอ) | ตรวจ scope ของ PAT |
| `publisher.py` คืน BLOCKED | ไม่มี OAuth client | รันข้อ 1 |
| IG Reels คืน BLOCKED | ไม่ได้ตั้ง `AX_PUBLIC_BASE` | ตั้งค่าเป็น public URL |
| หน้า `/connect` เปิดไม่ได้ | runtime URL เปลี่ยน | ใช้ `PUBLIC_URL` ปัจจุบัน หรือวิธี B (command line) |

---

## ข้อจำกัดที่ซื่อสัตย์

- ไม่มีแพลตฟอร์มไหนให้อัปโหลดแบบไม่ระบุตัวตน — AX ทำงานนี้แทนไม่ได้
- Monetization (YouTube Partner Program) ต้องมี 1,000 subscribers และ
  10M Shorts views ใน 90 วัน + AdSense ที่อนุมัติในนาม K
  AX เปิด AdSense แทนให้ไม่ได้
- รายได้ที่รายงานจะนับเฉพาะ `CASH RECEIVED` เท่านั้น
