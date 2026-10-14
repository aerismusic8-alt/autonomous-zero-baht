#!/usr/bin/env bash
# Sync this lab into the GitHub repo and push.
#
# Works the moment K provides a write-scoped token:
#   python3 pipeline/connect.py github --token github_pat_XXXX
#
# Reads the token from secrets/github_pat.txt (preferred) or $GITHUB_TOKEN.
# Never echoes the token.
set -u

LAB_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO="${AX_REPO:-aerismusic8-alt/autonomous-zero-baht}"
SUBDIR="${AX_SUBDIR:-ax-content-lab}"
BRANCH="${AX_BRANCH:-ax-content-lab}"

TOKEN=""
if [ -f "$LAB_DIR/secrets/github_pat.txt" ]; then
  TOKEN="$(tr -d '\n\r' < "$LAB_DIR/secrets/github_pat.txt")"
elif [ -n "${GITHUB_TOKEN:-}" ]; then
  TOKEN="$GITHUB_TOKEN"
fi

if [ -z "$TOKEN" ]; then
  echo "[sync] BLOCKED: no write token. Run: python3 pipeline/connect.py github --token <PAT>"
  echo "[sync] See docs/SETUP_FOR_K.md item 1."
  exit 2
fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "[sync] cloning $REPO"
git clone --quiet "https://${TOKEN}@github.com/${REPO}.git" "$WORK/repo" || {
  echo "[sync] BLOCKED: clone failed (check token scope: Contents = Read and write)"; exit 3; }

cd "$WORK/repo" || exit 3
git checkout --quiet -B "$BRANCH"

mkdir -p "$SUBDIR"
# copy code + evidence, never secrets
for item in pipeline content research docs brand .github README.md AGENTS.md run_loop.sh .gitignore; do
  [ -e "$LAB_DIR/$item" ] && cp -r "$LAB_DIR/$item" "$SUBDIR/"
done
rm -rf "$SUBDIR/secrets" "$SUBDIR"/content/*/assets

# keep only evidence-relevant media, and only the first time (v1.0 evidence set)
if ! git ls-tree -r --name-only HEAD "$SUBDIR" 2>/dev/null | grep -q 'final.mp4'; then
  echo "[sync] first push: including v1.0 video evidence"
else
  rm -f "$SUBDIR"/content/*/final.mp4
fi

git add -A
if git diff --cached --quiet; then
  echo "[sync] nothing to commit"
else
  git -c user.name="ax-lab-bot" -c user.email="openhands@all-hands.dev" \
      commit --quiet -m "chore(ax-lab): sync loop evidence $(date -u +%FT%TZ)"
fi

echo "[sync] pushing to $BRANCH"
if git push --quiet origin "$BRANCH" 2>&1; then
  echo "[sync] OK -> https://github.com/${REPO}/tree/${BRANCH}/${SUBDIR}"
else
  echo "[sync] BLOCKED: push rejected (token lacks Contents: Read and write)"
  exit 4
fi
