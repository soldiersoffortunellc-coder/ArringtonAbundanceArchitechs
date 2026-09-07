import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { computeSegmentValue, computeScenario, computeAllScenarios } from '../src/revenue/financialModel.js';
import scenariosConfig from '../config/scenarios/90-day-revenue-scenarios.json' with { type: 'json' };

describe('financialModel: revenue calculations', () => {
  test('computeSegmentValue matches the premium-implementation target figures from the brief', () => {
    const result = computeSegmentValue({ clients: 25, setupFee: 20000, monthlyFee: 3500, recurringMonths: 3 });
    assert.equal(result.setupRevenue, 500000);
    assert.equal(result.recurringRevenue, 262500);
    assert.equal(result.total, 762500);
  });

  test('computeSegmentValue matches the standardized-SaaS target figures from the brief', () => {
    const result = computeSegmentValue({ clients: 50, setupFee: 2500, monthlyFee: 997, recurringMonths: 3 });
    assert.equal(result.setupRevenue, 125000);
    assert.equal(result.recurringRevenue, 149550);
    assert.equal(result.total, 274550);
  });

  test('computeSegmentValue rejects negative clients', () => {
    assert.throws(() => computeSegmentValue({ clients: -1, setupFee: 1, monthlyFee: 1, recurringMonths: 1 }));
  });

  test('target scenario combined total equals $1,037,050 (brief\'s exact combined figure)', () => {
    const result = computeScenario({
      segments: scenariosConfig.segments,
      scenario: scenariosConfig.scenarios.target,
      recurringMonthsModeled: scenariosConfig.recurringMonthsModeled,
    });
    assert.equal(result.total, 1037050);
  });

  test('computeAllScenarios returns conservative < target < aggressive', () => {
    const all = computeAllScenarios(scenariosConfig);
    assert.ok(all.conservative.total < all.target.total);
    assert.ok(all.target.total < all.aggressive.total);
    assert.equal(all.target.total, 1037050);
  });
});
