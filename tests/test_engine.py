import json
import tempfile
import unittest
from pathlib import Path

from engine.content import create_draft
from engine.decision import record_decision
from engine.validator import validate_drafts

class EngineTests(unittest.TestCase):
    def test_no_payment_guard_config(self):
        cfg = json.loads((Path(__file__).parents[1] / "config" / "system.json").read_text(encoding="utf-8-sig"))
        self.assertTrue(cfg["no_payment_guard"])
        self.assertEqual(cfg["budget_thb"], 0)

    def test_draft_has_disclosure_and_no_first_hand_claim(self):
        draft = create_draft({
            "title": "Test topic",
            "url": "https://example.com/source",
            "summary": "Verified source summary",
            "source": "https://example.com/feed",
            "score": 1
        })
        self.assertFalse(draft["first_hand_experience_claimed"])
        self.assertTrue(draft["formats"]["affiliate_disclosure"])

    def test_validator_passes_valid_draft(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p = root / "draft.json"
            p.write_text(json.dumps({
                "source_url": "https://example.com/source",
                "status": "draft_requires_human_review",
                "first_hand_experience_claimed": False,
                "formats": {
                    "affiliate_disclosure": "Disclosure",
                    "seo_article_outline": {"sections": ["a"]}
                }
            }))
            old = __import__("engine.validator", fromlist=["ROOT"]).ROOT
            import engine.validator as validator
            validator.ROOT = root
            try:
                result = validate_drafts(["draft.json"])
                self.assertTrue(result[0]["passed"])
            finally:
                validator.ROOT = old

    def test_decision_never_auto_publishes(self):
        record = record_decision(1, 1, [{"passed": True}])
        self.assertFalse(record["publish_automatically"])

if __name__ == "__main__":
    unittest.main()
