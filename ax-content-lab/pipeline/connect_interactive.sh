#!/usr/bin/env bash
# Interactive credential intake. Nothing is echoed to the screen or to chat.
#
# Run:   bash pipeline/connect_interactive.sh
#
# It prompts for (all optional - press Enter to skip):
#   1. GitHub PAT with repo write scope
#   2. Path to a downloaded YouTube OAuth client JSON
#
# Secrets are written to secrets/ (chmod 600, git-ignored) and never printed.
set -u
cd "$(dirname "$0")/.."

echo "=============================================="
echo " AX Content Lab - credential intake"
echo " Nothing you type is displayed or logged."
echo "=============================================="
echo

# --- GitHub ---------------------------------------------------------------
read -r -s -p "1) Paste GitHub PAT (github_pat_...), or press Enter to skip: " GH
echo
if [ -n "${GH:-}" ]; then
  if [ -f secrets/github_pat.txt ]; then
    echo "   (replacing existing secrets/github_pat.txt)"
  fi
  python3 - "$GH" <<'PY'
import os, stat, sys
os.makedirs("secrets", exist_ok=True)
try: os.chmod("secrets", 0o700)
except OSError: pass
p = os.path.join("secrets", "github_pat.txt")
with open(p, "w") as f:
    f.write(sys.argv[1].strip() + "\n")
os.chmod(p, stat.S_IRUSR | stat.S_IWUSR)
print("   stored ->", p, "(mode 600)")
PY
  unset GH
else
  echo "   skipped GitHub"
fi
echo

# --- YouTube --------------------------------------------------------------
read -r -p "2) Path to YouTube OAuth client JSON, or press Enter to skip: " YT
if [ -n "${YT:-}" ]; then
  if [ -f "$YT" ]; then
    python3 pipeline/connect.py youtube --client "$YT"
  else
    echo "   file not found: $YT"
  fi
else
  echo "   skipped YouTube"
fi
echo

echo "=============================================="
echo " Verifying connections..."
echo "=============================================="
python3 pipeline/connect.py check
echo
echo "If GitHub shows \"can_push\": true, run:"
echo "   bash pipeline/sync_repo.sh"
