import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { AiUsageLimiter } from '../src/agents/aiUsageLimiter.js';

describe('AI usage limits', () => {
  test('flags a client as over limit once usage exceeds the monthly cap', () => {
    const limiter = new AiUsageLimiter({ monthlyLimit: 100 });
    limiter.recordUsage('c1', 90);
    assert.equal(limiter.isOverLimit('c1'), false);
    assert.equal(limiter.remaining('c1'), 10);

    const result = limiter.recordUsage('c1', 20);
    assert.equal(result.overLimit, true);
    assert.equal(limiter.isOverLimit('c1'), true);
  });

  test('tracks usage independently per client', () => {
    const limiter = new AiUsageLimiter({ monthlyLimit: 50 });
    limiter.recordUsage('c1', 40);
    limiter.recordUsage('c2', 10);
    assert.equal(limiter.usage('c1'), 40);
    assert.equal(limiter.usage('c2'), 10);
  });

  test('resetMonthly clears usage for a new billing cycle', () => {
    const limiter = new AiUsageLimiter({ monthlyLimit: 10 });
    limiter.recordUsage('c1', 15);
    assert.equal(limiter.isOverLimit('c1'), true);
    limiter.resetMonthly();
    assert.equal(limiter.usage('c1'), 0);
    assert.equal(limiter.isOverLimit('c1'), false);
  });

  test('rejects a non-positive monthly limit', () => {
    assert.throws(() => new AiUsageLimiter({ monthlyLimit: 0 }));
  });
});
