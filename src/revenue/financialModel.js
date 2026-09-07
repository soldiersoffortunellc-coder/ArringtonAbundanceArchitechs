// 90-day financial model — computes modeled scenario values from client
// counts and per-segment economics. Never presents output as guaranteed;
// callers are responsible for labeling output as a planning target.
// See docs/04-financial-model.md.

/**
 * @param {{clients:number, setupFee:number, monthlyFee:number, recurringMonths:number}} input
 */
export function computeSegmentValue({ clients, setupFee, monthlyFee, recurringMonths }) {
  if (clients < 0) throw new Error('clients must be >= 0');
  if (setupFee < 0 || monthlyFee < 0) throw new Error('fees must be >= 0');
  if (recurringMonths < 0) throw new Error('recurringMonths must be >= 0');

  const setupRevenue = clients * setupFee;
  const recurringRevenue = clients * monthlyFee * recurringMonths;
  return {
    clients,
    setupRevenue,
    recurringRevenue,
    total: setupRevenue + recurringRevenue,
  };
}

/**
 * @param {{segments: Record<string, {setupFee:number, monthlyFee:number}>, scenario: {clients: Record<string, number>}, recurringMonthsModeled: number}} input
 */
export function computeScenario({ segments, scenario, recurringMonthsModeled }) {
  const bySegment = {};
  let total = 0;
  for (const [segmentId, segmentDef] of Object.entries(segments)) {
    const clients = scenario.clients[segmentId] ?? 0;
    const result = computeSegmentValue({
      clients,
      setupFee: segmentDef.setupFee,
      monthlyFee: segmentDef.monthlyFee,
      recurringMonths: recurringMonthsModeled,
    });
    bySegment[segmentId] = result;
    total += result.total;
  }
  return { bySegment, total };
}

/**
 * @param {{segments: object, scenarios: Record<string, object>, recurringMonthsModeled: number}} scenariosConfig
 * Matches the shape of config/scenarios/90-day-revenue-scenarios.json.
 */
export function computeAllScenarios(scenariosConfig) {
  const { segments, scenarios, recurringMonthsModeled } = scenariosConfig;
  const result = {};
  for (const [scenarioId, scenarioDef] of Object.entries(scenarios)) {
    result[scenarioId] = computeScenario({ segments, scenario: scenarioDef, recurringMonthsModeled });
  }
  return result;
}
