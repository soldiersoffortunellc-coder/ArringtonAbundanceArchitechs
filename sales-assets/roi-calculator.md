# ROI Calculator — Methodology

Implementation: `src/sales/roiCalculator.js` (tested in
`tests/roiCalculator.test.js`). This doc explains the model; the code
computes it from the prospect's own numbers collected on the qualification
form — **never from assumed industry averages presented as their result.**

## Inputs (from the qualification form)

- `leadsOrCallsPerWeek`
- `currentResponseRateOrConversionPct` (their own estimate)
- `averageTicketValue`
- `estimatedMissedOrUnconvertedPct` (their own estimate of what's slipping
  through today — e.g., missed calls, unsold estimates, cold leads)
- `offerMonthlyFee` (from the tier being proposed)

## Calculation

```
recoverableUnitsPerMonth = leadsOrCallsPerWeek * 4.33 * estimatedMissedOrUnconvertedPct
recoverableUnitsCaptured = recoverableUnitsPerMonth * assumedRecoveryRate   // configurable, default 0.30 — conservative, disclosed
additionalMonthlyRevenue = recoverableUnitsCaptured * averageTicketValue
monthlyRoiMultiple = additionalMonthlyRevenue / offerMonthlyFee
paybackMonths = offerSetupFee / max(additionalMonthlyRevenue - offerMonthlyFee, epsilon)
```

## Presentation rule

Always show the `assumedRecoveryRate` assumption on-screen next to the
result, and always label the output "Estimated potential impact based on
your numbers and a conservative 30% recovery assumption" — never "Your
ROI will be X." This keeps the calculator consistent with the brief's rule
against representing projections as guarantees.

## Where it's used

Discovery/demo close, and as a proposal-template exhibit
(`sales-assets/proposal-template.md`).
