import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def record_metrics(content_ids):
    records = []
    for content_id in content_ids:
        records.append({
            "content_id": content_id, "impressions": None, "clicks": None,
            "conversions": None, "revenue": None, "currency": None,
            "verified": False, "source": None,
            "recorded_at": datetime.now(timezone.utc).isoformat()
        })
    out = ROOT / "data" / "analytics"
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return records
