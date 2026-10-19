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
# Base on the existing remote branch when it exists, so pushes fast-forward.
if git fetch --quiet origin "$BRANCH" 2>/dev/null; then
  git checkout --quiet -B "$BRANCH" "origin/$BRANCH"
else
  git checkout --quiet -B "$BRANCH"
fi

mkdir -p "$SUBDIR"
# copy code + evidence, never secrets
for item in pipeline content research docs brand .github README.md AGENTS.md run_loop.sh .gitignore site; do
  [ -e "$LAB_DIR/$item" ] && cp -r "$LAB_DIR/$item" "$SUBDIR/"
done
rm -rf "$SUBDIR/secrets" "$SUBDIR"/content/*/assets

# GitHub Actions only reads `.github/workflows/` at the REPOSITORY ROOT. The lab
# keeps its canonical workflow inside `$SUBDIR/.github/workflows/`, which GitHub
# would otherwise ignore. Install it at the root so the loop actually runs.
mkdir -p .github/workflows
cp "$LAB_DIR/.github/workflows/lab-loop.yml" .github/workflows/ax-lab-loop.yml

# Videos are gitignored in the lab, so they need a one-time force-add. Once they
# are tracked in the repo they stay tracked; never delete them from disk (that
# would stage a deletion and drop the evidence).
if git ls-tree -r --name-only HEAD "$SUBDIR" 2>/dev/null | grep -q 'final.mp4'; then
  echo "[sync] videos already in repo: keeping tracked evidence"
else
  echo "[sync] first push: force-adding v1.0 video evidence"
fi

git add -A
git add -f "$SUBDIR"/content/*/final.mp4 2>/dev/null || true
git add -f "$SUBDIR"/brand/*.png 2>/dev/null || true
if git diff --cached --quiet; then
  echo "[sync] nothing to commit"
else
  git -c user.name="ax-lab-bot" -c user.email="openhands@all-hands.dev" \
      commit --quiet -m "chore(ax-lab): sync loop evidence $(date -u +%FT%TZ)"
fi

echo "[sync] pushing to $BRANCH"
PUSH_OUT="$(git push --quiet origin "$BRANCH" 2>&1)"
if [ $? -eq 0 ]; then
  echo "[sync] OK -> https://github.com/${REPO}/tree/${BRANCH}/${SUBDIR}"
  exit 0
fi
echo "$PUSH_OUT"

# A token without the fine-grained "Workflows" permission cannot create or update
# any file under .github/workflows/. That rejects the WHOLE push, which would also
# lose the code and evidence. Retry without the workflow changes so the rest
# persists, and report the workflow blocker separately.
if printf '%s' "$PUSH_OUT" | grep -qi 'workflow'; then
  echo "[sync] NOTE: token cannot write .github/workflows/ (needs fine-grained 'Workflows: Read and write')."
  echo "[sync]       Retrying without workflow changes so code + evidence still persist."
  git rm --quiet --cached .github/workflows/ax-lab-loop.yml 2>/dev/null || true
  rm -f .github/workflows/ax-lab-loop.yml
  git reset --quiet HEAD -- .github/workflows 2>/dev/null || true
  git checkout --quiet HEAD -- "$SUBDIR/.github/workflows" 2>/dev/null || true
  git add -A
  if git diff --cached --quiet; then
    echo "[sync] nothing left to commit"
    exit 0
  fi
  git -c user.name="ax-lab-bot" -c user.email="openhands@all-hands.dev" \
      commit --quiet --amend -m "chore(ax-lab): sync loop evidence $(date -u +%FT%TZ)"
  if git push --quiet origin "$BRANCH" 2>&1; then
    echo "[sync] OK (code + evidence) -> https://github.com/${REPO}/tree/${BRANCH}/${SUBDIR}"
    echo "[sync] BLOCKED: CI workflow not updated - K must grant the PAT the"
    echo "[sync]          fine-grained 'Workflows: Read and write' permission."
    exit 0
  fi
  echo "[sync] BLOCKED: push rejected (token lacks Contents: Read and write)"
  exit 4
fi

echo "[sync] BLOCKED: push rejected (token lacks Contents: Read and write)"
exit 4
