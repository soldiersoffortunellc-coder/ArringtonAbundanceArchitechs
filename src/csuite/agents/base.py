"""
Base class for every task-oriented agent in the C-Suite AI Agent System.

Every agent:
  - has an explicit title, mission, and list of KPIs it owns
  - declares which GHL directive kinds it is allowed to issue (its "authority")
  - implements run(context) -> AgentReport, a pure function of the context
    dict it is given plus whatever adapters/registries it was constructed with
  - never invents facts: any number it reports comes from a config file, a
    passed-in dataset, or a computation over those — never a hallucinated
    guess dressed up as data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentReport:
    agent: str
    title: str
    decisions: list = field(default_factory=list)
    directives_issued: list = field(default_factory=list)  # GHL action_ids or descriptions
    kpis: dict = field(default_factory=dict)
    escalations: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "agent": self.agent,
            "title": self.title,
            "decisions": self.decisions,
            "directives_issued": self.directives_issued,
            "kpis": self.kpis,
            "escalations": self.escalations,
            "warnings": self.warnings,
        }


class BaseAgent:
    name: str = "base_agent"
    title: str = "Base Agent"
    mission: str = ""
    kpis_owned: list[str] = []
    ghl_authority: list[str] = []  # which GHLAdapter action kinds this agent may direct

    def __init__(self, adapter=None, global_controls=None):
        self.adapter = adapter
        self.global_controls = global_controls

    def _guard(self) -> None:
        if self.global_controls is not None:
            self.global_controls.guard()

    def run(self, context: dict) -> AgentReport:  # pragma: no cover - abstract
        raise NotImplementedError

    def new_report(self) -> AgentReport:
        return AgentReport(agent=self.name, title=self.title)
