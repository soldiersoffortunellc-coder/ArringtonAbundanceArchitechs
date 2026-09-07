import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { estimateRoi } from '../src/sales/roiCalculator.js';

describe('ROI calculator', () => {
  test('computes additional monthly revenue from the prospect\'s own numbers', () => {
    const result = estimateRoi({
      leadsOrCallsPerWeek: 20,
      estimatedMissedOrUnconvertedPct: 0.25,
      averageTicketValue: 500,
      offerMonthlyFee: 997,
      offerSetupFee: 2500,
      assumedRecoveryRate: 0.3,
    });
    // recoverableUnitsPerMonth = 20 * 4.33 * 0.25 = 21.65
    // captured = 21.65 * 0.3 = 6.495
    // additionalMonthlyRevenue = 6.495 * 500 = 3247.5
    assert.ok(Math.abs(result.additionalMonthlyRevenue - 3247.5) < 1e-9);
    assert.match(result.disclosure, /not a guaranteed result/i);
  });

  test('always discloses the recovery-rate assumption', () => {
    const result = estimateRoi({
      leadsOrCallsPerWeek: 10,
      estimatedMissedOrUnconvertedPct: 0.5,
      averageTicketValue: 300,
      offerMonthlyFee: 697,
    });
    assert.match(result.disclosure, /30% recovery assumption/);
  });

  test('rejects an out-of-range percentage', () => {
    assert.throws(() => estimateRoi({
      leadsOrCallsPerWeek: 10, estimatedMissedOrUnconvertedPct: 1.5, averageTicketValue: 100, offerMonthlyFee: 100,
    }));
  });
});
