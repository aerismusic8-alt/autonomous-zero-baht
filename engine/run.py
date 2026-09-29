import json
from pathlib import Path
from .logger import log_event
from .research import run_research
from .content import generate_drafts
from .validator import validate_drafts
from .decision import record_decision
from .publisher import publish_drafts
from .analytics import record_metrics

ROOT = Path(__file__).resolve().parents[1]

def main():
    config = json.loads((ROOT / "config" / "system.json").read_text(encoding="utf-8-sig"))
    providers = json.loads((ROOT / "config" / "providers.json").read_text(encoding="utf-8-sig"))
    if config.get("no_payment_guard") is not True or config.get("budget_thb") != 0:
        raise RuntimeError("NO-PAYMENT GUARD: configuration must explicitly enforce zero spending.")
    log_event("run_started", project=config.get("project"), mode=config.get("mode"), budget_thb=0)
    try:
        opportunities = run_research(config)
    except Exception as exc:
        opportunities = []
        log_event("research_engine_failed", error=type(exc).__name__, detail=str(exc)[:250])
    drafts = generate_drafts(opportunities, int(config.get("max_drafts_per_run", 5))) if opportunities else []
    validations = validate_drafts(drafts)
    decision = record_decision(len(opportunities), len(drafts), validations)
    valid_drafts = [p for p, v in zip(drafts, validations) if v["passed"]]
    publish_cfg = providers.get("publishing", {})
    publish_result = publish_drafts(valid_drafts, publish_cfg)
    analytics_cfg = providers.get("analytics", {})
    if analytics_cfg.get("enabled", True):
        record_metrics([Path(p).stem for p in valid_drafts])
    log_event("run_completed", research_count=len(opportunities), draft_count=len(drafts),
              published=publish_result["published"], next_action=decision["recommended_action"])

if __name__ == "__main__":
    main()
