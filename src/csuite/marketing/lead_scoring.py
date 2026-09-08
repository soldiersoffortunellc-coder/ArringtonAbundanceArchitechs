"""
Generic behavior-based lead-scoring engine, configured by
config/marketing/idecide/lead_scoring.json. Used by the Lead-Conversion
Director for iDecide viewer sessions, and reusable for any other
event-scored engagement stream.

Per the spec: repeat completions are RECORDED, never auto-scored as higher
intent — 'repeat_completion' defaults to a 0-point event in config, and
repeat activity is exposed as a fact (`repeat_completion_count`) for the
qualification agent to evaluate in context, not a multiplier this engine
applies on its own.
"""

from __future__ import annotations

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "marketing" / "idecide" / "lead_scoring.json"


def _load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


class LeadScoringEngine:
    def __init__(self, config: dict | None = None):
        self.config = config or _load_config()
        self.event_scores: dict[str, int] = self.config["event_scores"]
        self.classifications: list[dict] = self.config["classifications"]
        self.floor = self.config["score_floor"]
        self.ceiling = self.config["score_ceiling"]

    def score(self, events: list[str]) -> dict:
        raw = sum(self.event_scores.get(e, 0) for e in events)
        clamped = max(self.floor, min(self.ceiling, raw))
        classification = next(
            (c["label"] for c in self.classifications if c["min"] <= clamped <= c["max"]),
            "Unclassified",
        )
        repeat_completions = events.count("repeat_completion")
        return {
            "raw_score": raw,
            "score": clamped,
            "classification": classification,
            "events_counted": list(events),
            "repeat_completion_count": repeat_completions,
            "repeat_completion_note": (
                "Repeat completions are recorded, not automatically scored higher — "
                "evaluate in context before treating as increased intent."
            ) if repeat_completions else None,
        }
