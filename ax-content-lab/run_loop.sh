#!/usr/bin/env bash
# AX Viral Content Lab — one full loop, end to end.
# Idempotent and safe to run on a schedule (cron / GitHub Actions / OpenHands).
set -u

cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$PATH"
STAMP="$(date -u +%FT%TZ)"
echo "[ax-lab] loop start $STAMP"

step() { echo "[ax-lab] -> $1"; }

step "research (public metadata only)"
python3 pipeline/research.py --label loop --limit 20 --enrich 6 \
  --queries "scary stories shorts" "space facts shorts" \
            "unsolved mystery shorts" "what if physics shorts" || true
python3 pipeline/analyze.py > research/analysis_latest.md 2>/dev/null || true

step "reference videos (real high performers, links for K)"
python3 pipeline/references.py --per-query 4 >/dev/null 2>&1 || true
python3 pipeline/build_refs_page.py >/dev/null 2>&1 || true
python3 pipeline/build_gallery_md.py >/dev/null 2>&1 || true

step "generate specs for new series entries"
python3 pipeline/gen_specs.py >/dev/null || true

step "produce + quality control"
python3 pipeline/batch.py --workers 3 || true

step "sync state store"
python3 pipeline/store.py sync

step "publish to every ready platform (no-op until credentials exist)"
python3 pipeline/multipost.py --all || true

step "scheduled posting tick (posts only inside a due slot)"
python3 pipeline/schedule.py --tick || true

step "analytics"
python3 pipeline/analytics.py || true

step "status report"
python3 pipeline/report.py

echo "[ax-lab] loop end $(date -u +%FT%TZ)"
