"""
Billing ledger: keeps contracted revenue, invoiced revenue, cash collected,
MRR, accounts receivable and refunds as distinct, never-conflated numbers,
per operating rules ("Never combine contracted revenue and collected revenue
into one misleading number").
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BillingEvent:
    tenant_id: str
    event_type: str  # "contract_signed" | "invoice_sent" | "payment_collected" | "refund"
    amount: float
    is_recurring: bool = False


class BillingLedger:
    def __init__(self):
        self.events: list[BillingEvent] = []

    def record(self, tenant_id: str, event_type: str, amount: float, is_recurring: bool = False) -> BillingEvent:
        event = BillingEvent(tenant_id=tenant_id, event_type=event_type, amount=amount, is_recurring=is_recurring)
        self.events.append(event)
        return event

    def contracted_revenue(self) -> float:
        return sum(e.amount for e in self.events if e.event_type == "contract_signed")

    def invoiced_revenue(self) -> float:
        return sum(e.amount for e in self.events if e.event_type == "invoice_sent")

    def cash_collected(self) -> float:
        return sum(e.amount for e in self.events if e.event_type == "payment_collected")

    def refunds(self) -> float:
        return sum(e.amount for e in self.events if e.event_type == "refund")

    def monthly_recurring_revenue(self) -> float:
        return sum(e.amount for e in self.events if e.event_type == "payment_collected" and e.is_recurring)

    def accounts_receivable(self) -> float:
        return max(self.invoiced_revenue() - self.cash_collected(), 0.0)

    def net_cash_collected(self) -> float:
        return self.cash_collected() - self.refunds()

    def summary(self) -> dict:
        return {
            "contracted_revenue": self.contracted_revenue(),
            "invoiced_revenue": self.invoiced_revenue(),
            "cash_collected": self.cash_collected(),
            "refunds": self.refunds(),
            "net_cash_collected": self.net_cash_collected(),
            "monthly_recurring_revenue": self.monthly_recurring_revenue(),
            "accounts_receivable": self.accounts_receivable(),
        }
