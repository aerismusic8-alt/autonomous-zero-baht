import json
import tempfile
import unittest
from pathlib import Path

import engine.analytics as analytics
from engine.publisher import publish_drafts

class NextPhaseTests(unittest.TestCase):
    def test_publisher_is_inert_by_default(self):
        result = publish_drafts(["draft"], {"publishing": {"enabled": False, "requires_human_review": True}})
        self.assertEqual(result["published"], 0)
        self.assertEqual(result["reason"], "publishing_disabled")

    def test_human_review_blocks_publishing(self):
        result = publish_drafts(["draft"], {"publishing": {"enabled": True, "requires_human_review": True}})
        self.assertEqual(result["published"], 0)
        self.assertEqual(result["reason"], "human_review_required")

    def test_metrics_start_unverified(self):
        with tempfile.TemporaryDirectory() as td:
            old = analytics.ROOT
            analytics.ROOT = Path(td)
            try:
                rows = analytics.record_metrics(["c1"])
                self.assertFalse(rows[0]["verified"])
                self.assertIsNone(rows[0]["revenue"])
                self.assertTrue((Path(td) / "data" / "analytics" / "metrics.json").exists())
            finally:
                analytics.ROOT = old

if __name__ == "__main__":
    unittest.main()
