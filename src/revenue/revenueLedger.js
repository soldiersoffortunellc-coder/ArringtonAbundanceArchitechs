// Contracted-vs-collected revenue ledger. Per docs/04-financial-model.md:
// "Never combine contracted revenue and collected revenue into one
// misleading number" — this class never exposes a method that sums the two.

const BILLING_EVENT_TYPES = ['invoice', 'payment', 'refund'];

export class RevenueLedger {
  constructor() {
    this.entries = [];
    this.mrrByClient = new Map();
  }

  recordContract({ clientId, amount, date = new Date() }) {
    this._assertAmount(amount);
    this._push('contract', { clientId, amount, date });
  }

  /** Handles invoice / payment (cash collected) / refund events uniformly. */
  recordBillingEvent({ type, clientId, amount, date = new Date() }) {
    if (!BILLING_EVENT_TYPES.includes(type)) {
      throw new Error(`Unknown billing event type: ${type}`);
    }
    this._assertAmount(amount);
    this._push(type, { clientId, amount, date });
  }

  recordCost({ clientId, amount, category, date = new Date() }) {
    this._assertAmount(amount);
    this._push('cost', { clientId, amount, category, date });
  }

  setMrr(clientId, amount, active = true) {
    this.mrrByClient.set(clientId, { amount, active });
  }

  _assertAmount(amount) {
    if (typeof amount !== 'number' || Number.isNaN(amount) || amount < 0) {
      throw new Error(`amount must be a non-negative number, got ${amount}`);
    }
  }

  _push(type, data) {
    this.entries.push({ type, ...data });
  }

  _sum(type) {
    return this.entries.filter((e) => e.type === type).reduce((s, e) => s + e.amount, 0);
  }

  contractedTotal() {
    return this._sum('contract');
  }

  invoicedTotal() {
    return this._sum('invoice');
  }

  collectedTotal() {
    return this._sum('payment');
  }

  refundsTotal() {
    return this._sum('refund');
  }

  accountsReceivable() {
    return this.invoicedTotal() - this.collectedTotal();
  }

  grossRevenue() {
    return this.collectedTotal() - this.refundsTotal();
  }

  fulfillmentCostTotal() {
    return this._sum('cost');
  }

  grossProfit() {
    return this.grossRevenue() - this.fulfillmentCostTotal();
  }

  mrr() {
    let total = 0;
    for (const { amount, active } of this.mrrByClient.values()) {
      if (active) total += amount;
    }
    return total;
  }
}
