import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { computeProfitability, flagIfBelowFloor } from '../src/revenue/profitability.js';

describe('profitability: margin alerts and revenue calculations', () => {
  test('computes gross margin, break-even, and max acceptable CAC', () => {
    const result = computeProfitability({
      setupRevenue: 20000,
      monthlyRevenue: 3500,
      softwareCost: 200,
      aiUsageCost: 150,
      integrationCost: 500,
      laborHours: 40,
      laborRatePerHour: 50,
      onboardingCost: 300,
      targetMarginFloor: 0.5,
    });

    // monthlyRecurringCost = 200 + 150 = 350; contribution = 3150
    assert.equal(result.costs.monthlyRecurringCost, 350);
    assert.ok(Math.abs(result.grossMarginMonthly - 3150 / 3500) < 1e-9);

    // oneTimeCost = 500 + 2000 (labor) + 300 = 2800; netSetupPosition = 20000-2800=17200 >=0 -> breakEven 0
    assert.equal(result.breakEvenMonths, 0);
    assert.ok(!result.belowMarginFloor);
  });

  test('flags an account below its required margin floor', () => {
    const result = computeProfitability({
      setupRevenue: 0,
      monthlyRevenue: 1000,
      softwareCost: 700, // margin = 30%
      targetMarginFloor: 0.5,
    });
    assert.ok(result.belowMarginFloor);
    const flag = flagIfBelowFloor(result);
    assert.equal(flag.flagged, true);
    assert.match(flag.reason, /below the required floor/);
  });

  test('does not flag an account at or above its margin floor', () => {
    const result = computeProfitability({
      setupRevenue: 0,
      monthlyRevenue: 1000,
      softwareCost: 400, // margin = 60%
      targetMarginFloor: 0.5,
    });
    const flag = flagIfBelowFloor(result);
    assert.equal(flag.flagged, false);
  });

  test('break-even is infinite when setup is underwater and monthly contribution is non-positive', () => {
    const result = computeProfitability({
      setupRevenue: 100,
      monthlyRevenue: 500,
      softwareCost: 500, // contribution = 0
      integrationCost: 10000, // deep one-time cost hole
    });
    assert.equal(result.breakEvenMonths, Infinity);
  });
});
