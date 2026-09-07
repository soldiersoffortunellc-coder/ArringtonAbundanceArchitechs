// AI usage limits guardrail — prevents runaway AI conversation/voice cost
// from eroding a client's margin. Per the brief's "AI usage limits"
// required test and docs/14-client-success-workflow.md margin monitoring.

export class AiUsageLimiter {
  /** @param {{monthlyLimit: number}} config */
  constructor({ monthlyLimit }) {
    if (monthlyLimit <= 0) throw new Error('monthlyLimit must be > 0');
    this.monthlyLimit = monthlyLimit;
    this.usageByClient = new Map();
  }

  recordUsage(clientId, units = 1) {
    if (units < 0) throw new Error('units must be >= 0');
    const current = this.usageByClient.get(clientId) ?? 0;
    const next = current + units;
    this.usageByClient.set(clientId, next);
    return { usage: next, limit: this.monthlyLimit, overLimit: next > this.monthlyLimit };
  }

  usage(clientId) {
    return this.usageByClient.get(clientId) ?? 0;
  }

  isOverLimit(clientId) {
    return this.usage(clientId) > this.monthlyLimit;
  }

  remaining(clientId) {
    return Math.max(this.monthlyLimit - this.usage(clientId), 0);
  }

  /** Call at the start of each billing cycle. */
  resetMonthly() {
    this.usageByClient.clear();
  }
}
