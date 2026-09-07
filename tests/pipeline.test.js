import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { Opportunity, weightedPipelineValue, totalPipelineValue, closeRate, resultsByDimension } from '../src/pipeline/pipeline.js';

describe('sales pipeline', () => {
  test('closed_lost requires a stored loss reason', () => {
    const opp = new Opportunity({ id: 'o1', value: 5000 });
    assert.throws(() => opp.moveTo('closed_lost'));
    opp.moveTo('closed_lost', { lossReason: 'price' });
    assert.equal(opp.lossReason, 'price');
  });

  test('weighted pipeline value applies stage probability', () => {
    const opps = [
      new Opportunity({ id: 'o1', value: 1000, stage: 'proposal_sent' }), // 0.55
      new Opportunity({ id: 'o2', value: 2000, stage: 'closed_won' }), // 1.0
    ];
    assert.equal(totalPipelineValue(opps), 3000);
    assert.equal(weightedPipelineValue(opps), 1000 * 0.55 + 2000 * 1.0);
  });

  test('close rate = won / (won + lost)', () => {
    const opps = [
      new Opportunity({ id: 'o1', value: 1000, stage: 'closed_won' }),
      new Opportunity({ id: 'o2', value: 1000, stage: 'closed_won' }),
      (() => {
        const o = new Opportunity({ id: 'o3', value: 1000 });
        o.moveTo('closed_lost', { lossReason: 'timing' });
        return o;
      })(),
    ];
    assert.equal(closeRate(opps), 2 / 3);
  });

  test('results grouped by industry for the executive command center', () => {
    const opps = [
      new Opportunity({ id: 'o1', value: 1000, stage: 'closed_won', industry: 'insurance' }),
      new Opportunity({ id: 'o2', value: 2000, stage: 'qualified', industry: 'insurance' }),
      new Opportunity({ id: 'o3', value: 3000, stage: 'closed_won', industry: 'real-estate' }),
    ];
    const grouped = resultsByDimension(opps, 'industry');
    assert.equal(grouped.insurance.count, 2);
    assert.equal(grouped.insurance.value, 3000);
    assert.equal(grouped.insurance.wonCount, 1);
    assert.equal(grouped['real-estate'].wonCount, 1);
  });

  test('rejects an unknown stage', () => {
    assert.throws(() => new Opportunity({ id: 'o1', value: 1, stage: 'made_up_stage' }));
  });
});
