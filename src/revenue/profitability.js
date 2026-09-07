// Client profitability controls — margin, break-even, and max acceptable
// acquisition cost, per docs/03-offer-ladder.md and the brief's "Client
// Profitability Controls" requirement.

/**
 * @param {object} input
 * @param {number} input.setupRevenue
 * @param {number} input.monthlyRevenue
 * @param {number} [input.softwareCost]
 * @param {number} [input.aiUsageCost]
 * @param {number} [input.phoneCost]
 * @param {number} [input.emailCost]
 * @param {number} [input.smsCost]
 * @param {number} [input.integrationCost]
 * @param {number} [input.laborHours]
 * @param {number} [input.laborRatePerHour]
 * @param {number} [input.onboardingCost]
 * @param {number} [input.supportCost]
 * @param {number} [input.targetMarginFloor] - e.g. 0.5 for 50%
 */
export function computeProfitability(input) {
  const {
    setupRevenue,
    monthlyRevenue,
    softwareCost = 0,
    aiUsageCost = 0,
    phoneCost = 0,
    emailCost = 0,
    smsCost = 0,
    integrationCost = 0,
    laborHours = 0,
    laborRatePerHour = 0,
    onboardingCost = 0,
    supportCost = 0,
    targetMarginFloor = 0.5,
  } = input;

  const laborCost = laborHours * laborRatePerHour;
  const monthlyRecurringCost = softwareCost + aiUsageCost + phoneCost + emailCost + smsCost + supportCost;
  const oneTimeCost = integrationCost + laborCost + onboardingCost;

  const monthlyContribution = monthlyRevenue - monthlyRecurringCost;
  const grossMarginMonthly = monthlyRevenue > 0 ? monthlyContribution / monthlyRevenue : 0;

  // Net position immediately after setup (positive = setup revenue covered one-time cost).
  const netSetupPosition = setupRevenue - oneTimeCost;

  let breakEvenMonths;
  if (netSetupPosition >= 0) {
    breakEvenMonths = 0;
  } else if (monthlyContribution <= 0) {
    breakEvenMonths = Infinity;
  } else {
    breakEvenMonths = Math.abs(netSetupPosition) / monthlyContribution;
  }

  // Maximum acceptable CAC: the total 12-month contribution (setup net of
  // one-time cost, plus 12 months of monthly contribution) this account
  // can absorb as acquisition cost while still breaking even in year 1.
  const twelveMonthContribution = netSetupPosition + monthlyContribution * 12;
  const maxAcceptableCac = Math.max(twelveMonthContribution, 0);

  const belowMarginFloor = grossMarginMonthly < targetMarginFloor;

  return {
    setupRevenue,
    monthlyRevenue,
    costs: {
      softwareCost, aiUsageCost, phoneCost, emailCost, smsCost,
      integrationCost, laborCost, onboardingCost, supportCost,
      monthlyRecurringCost, oneTimeCost,
    },
    grossMarginMonthly,
    breakEvenMonths,
    maxAcceptableCac,
    targetMarginFloor,
    belowMarginFloor,
  };
}

/** Flags an account/package that falls below its required margin. */
export function flagIfBelowFloor(profitabilityResult) {
  if (!profitabilityResult.belowMarginFloor) {
    return { flagged: false };
  }
  return {
    flagged: true,
    reason: `Gross margin ${(profitabilityResult.grossMarginMonthly * 100).toFixed(1)}% is below the required floor of ${(profitabilityResult.targetMarginFloor * 100).toFixed(1)}%`,
  };
}
