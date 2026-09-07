import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { RevenueLedger } from '../src/revenue/revenueLedger.js';

describe('revenueLedger: contracted-vs-collected revenue and billing events', () => {
  test('contracted and collected revenue are tracked separately, never combined', () => {
    const ledger = new RevenueLedger();
    ledger.recordContract({ clientId: 'c1', amount: 20000 });
    ledger.recordBillingEvent({ type: 'payment', clientId: 'c1', amount: 5000 });

    assert.equal(ledger.contractedTotal(), 20000);
    assert.equal(ledger.collectedTotal(), 5000);
    assert.notEqual(ledger.contractedTotal(), ledger.collectedTotal());
    // No method on the ledger sums the two into one figure.
    assert.equal(typeof ledger.totalRevenue, 'undefined');
  });

  test('billing-event handling: invoice, payment, refund route independently', () => {
    const ledger = new RevenueLedger();
    ledger.recordBillingEvent({ type: 'invoice', clientId: 'c1', amount: 3500 });
    ledger.recordBillingEvent({ type: 'payment', clientId: 'c1', amount: 3500 });
    ledger.recordBillingEvent({ type: 'refund', clientId: 'c1', amount: 500 });

    assert.equal(ledger.invoicedTotal(), 3500);
    assert.equal(ledger.collectedTotal(), 3500);
    assert.equal(ledger.refundsTotal(), 500);
    assert.equal(ledger.grossRevenue(), 3000);
  });

  test('rejects an unknown billing event type', () => {
    const ledger = new RevenueLedger();
    assert.throws(() => ledger.recordBillingEvent({ type: 'bogus', clientId: 'c1', amount: 100 }));
  });

  test('accounts receivable = invoiced - collected', () => {
    const ledger = new RevenueLedger();
    ledger.recordBillingEvent({ type: 'invoice', clientId: 'c1', amount: 10000 });
    ledger.recordBillingEvent({ type: 'payment', clientId: 'c1', amount: 4000 });
    assert.equal(ledger.accountsReceivable(), 6000);
  });

  test('gross profit = gross revenue - fulfillment cost', () => {
    const ledger = new RevenueLedger();
    ledger.recordBillingEvent({ type: 'payment', clientId: 'c1', amount: 10000 });
    ledger.recordCost({ clientId: 'c1', amount: 3000, category: 'ai-usage' });
    ledger.recordCost({ clientId: 'c1', amount: 1000, category: 'labor' });
    assert.equal(ledger.grossProfit(), 6000);
  });

  test('MRR sums only active client subscriptions', () => {
    const ledger = new RevenueLedger();
    ledger.setMrr('c1', 997, true);
    ledger.setMrr('c2', 3500, true);
    ledger.setMrr('c3', 2500, false); // churned
    assert.equal(ledger.mrr(), 4497);
  });

  test('rejects a negative amount', () => {
    const ledger = new RevenueLedger();
    assert.throws(() => ledger.recordContract({ clientId: 'c1', amount: -1 }));
  });
});
