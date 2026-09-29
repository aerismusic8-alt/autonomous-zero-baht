from .logger import log_event


def publish_drafts(drafts, config):
    publishing = config.get("publishing", {})
    enabled = publishing.get("enabled", False)
    human_review = publishing.get("requires_human_review", True)
    if not enabled or human_review:
        reason = "publishing_disabled" if not enabled else "human_review_required"
        log_event("publisher_skipped", reason=reason, draft_count=len(drafts))
        return {"published": 0, "skipped": len(drafts), "reason": reason}
    log_event("publisher_blocked", reason="no_platform_adapter_enabled")
    return {"published": 0, "skipped": len(drafts), "reason": "no_platform_adapter_enabled"}
