// ROI calculator — always computed from a prospect's own numbers, never
// from assumed industry averages. See sales-assets/roi-calculator.md.

const WEEKS_PER_MONTH = 4.33;

/**
 * @param {object} input
 * @param {number} input.leadsOrCallsPerWeek
 * @param {number} input.estimatedMissedOrUnconvertedPct - 0..1
 * @param {number} input.averageTicketValue
 * @param {number} input.offerMonthlyFee
 * @param {number} [input.offerSetupFee]
 * @param {number} [input.assumedRecoveryRate] - default 0.30, disclosed in output
 */
export function estimateRoi({
  leadsOrCallsPerWeek,
  estimatedMissedOrUnconvertedPct,
  averageTicketValue,
  offerMonthlyFee,
  offerSetupFee = 0,
  assumedRecoveryRate = 0.3,
}) {
  if (leadsOrCallsPerWeek < 0) throw new Error('leadsOrCallsPerWeek must be >= 0');
  if (estimatedMissedOrUnconvertedPct < 0 || estimatedMissedOrUnconvertedPct > 1) {
    throw new Error('estimatedMissedOrUnconvertedPct must be between 0 and 1');
  }
  if (averageTicketValue < 0) throw new Error('averageTicketValue must be >= 0');

  const recoverableUnitsPerMonth = leadsOrCallsPerWeek * WEEKS_PER_MONTH * estimatedMissedOrUnconvertedPct;
  const recoverableUnitsCaptured = recoverableUnitsPerMonth * assumedRecoveryRate;
  const additionalMonthlyRevenue = recoverableUnitsCaptured * averageTicketValue;
  const netMonthlyImpact = additionalMonthlyRevenue - offerMonthlyFee;
  const monthlyRoiMultiple = offerMonthlyFee > 0 ? additionalMonthlyRevenue / offerMonthlyFee : null;
  const paybackMonths = netMonthlyImpact > 0 ? offerSetupFee / netMonthlyImpact : Infinity;

  return {
    assumedRecoveryRate,
    recoverableUnitsPerMonth,
    additionalMonthlyRevenue,
    netMonthlyImpact,
    monthlyRoiMultiple,
    paybackMonths,
    disclosure: `Estimated potential impact based on your numbers and a conservative ${Math.round(assumedRecoveryRate * 100)}% recovery assumption. Not a guaranteed result.`,
  };
}
