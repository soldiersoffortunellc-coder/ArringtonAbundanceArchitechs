// Sales pipeline — matches config/pipelines/sales-pipeline.json.
// docs/11-sales-pipeline.md.

export const STAGE_IDS = [
  'target_account', 'contacted', 'engaged', 'discovery_booked', 'discovery_completed',
  'qualified', 'demo_booked', 'demo_completed', 'proposal_sent', 'verbal_commitment',
  'payment_pending', 'closed_won', 'onboarding', 'implementation', 'quality_assurance',
  'live', 'expansion_opportunity', 'nurture', 'closed_lost',
];

export const DEFAULT_STAGE_PROBABILITIES = {
  target_account: 0.02, contacted: 0.05, engaged: 0.10, discovery_booked: 0.15,
  discovery_completed: 0.20, qualified: 0.30, demo_booked: 0.35, demo_completed: 0.45,
  proposal_sent: 0.55, verbal_commitment: 0.70, payment_pending: 0.85, closed_won: 1.0,
  onboarding: 1.0, implementation: 1.0, quality_assurance: 1.0, live: 1.0,
  expansion_opportunity: 0.25, nurture: 0.05, closed_lost: 0.0,
};

export class Opportunity {
  constructor({ id, value, stage = 'target_account', source, salesperson, industry }) {
    if (!STAGE_IDS.includes(stage)) throw new Error(`Unknown stage: ${stage}`);
    this.id = id;
    this.value = value;
    this.stage = stage;
    this.source = source;
    this.salesperson = salesperson;
    this.industry = industry;
    this.lossReason = null;
    this.history = [{ stage, at: new Date() }];
  }

  moveTo(stage, { lossReason, at = new Date() } = {}) {
    if (!STAGE_IDS.includes(stage)) throw new Error(`Unknown stage: ${stage}`);
    if (stage === 'closed_lost' && !lossReason) {
      throw new Error('closed_lost transition requires a lossReason');
    }
    if (stage === 'closed_lost') this.lossReason = lossReason;
    this.stage = stage;
    this.history.push({ stage, at, lossReason: stage === 'closed_lost' ? lossReason : undefined });
    return this;
  }
}

export function totalPipelineValue(opportunities) {
  return opportunities.reduce((sum, o) => sum + o.value, 0);
}

export function weightedPipelineValue(opportunities, stageProbabilities = DEFAULT_STAGE_PROBABILITIES) {
  return opportunities.reduce((sum, o) => sum + o.value * (stageProbabilities[o.stage] ?? 0), 0);
}

export function closeRate(opportunities) {
  const won = opportunities.filter((o) => o.stage === 'closed_won').length;
  const lost = opportunities.filter((o) => o.stage === 'closed_lost').length;
  const decided = won + lost;
  return decided === 0 ? 0 : won / decided;
}

export function resultsByDimension(opportunities, dimension) {
  const groups = {};
  for (const o of opportunities) {
    const key = o[dimension] ?? 'unknown';
    if (!groups[key]) groups[key] = { count: 0, value: 0, wonCount: 0 };
    groups[key].count += 1;
    groups[key].value += o.value;
    if (o.stage === 'closed_won') groups[key].wonCount += 1;
  }
  return groups;
}
