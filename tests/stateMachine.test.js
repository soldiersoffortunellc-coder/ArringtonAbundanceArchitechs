import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { OnboardingClient, MAIN_SEQUENCE } from '../src/onboarding/stateMachine.js';

describe('onboarding state machine: client onboarding transitions', () => {
  test('starts at PAYMENT_RECEIVED and allows forward main-sequence transitions', () => {
    const client = new OnboardingClient('c1');
    assert.equal(client.state, 'PAYMENT_RECEIVED');
    client.transitionTo('AGREEMENT_CONFIRMED');
    client.transitionTo('INTAKE_SENT');
    assert.equal(client.state, 'INTAKE_SENT');
  });

  test('rejects skipping ahead in the main sequence', () => {
    const client = new OnboardingClient('c1');
    assert.throws(() => client.transitionTo('SNAPSHOT_APPLIED'));
  });

  test('rejects an unknown state', () => {
    const client = new OnboardingClient('c1');
    assert.throws(() => client.transitionTo('NOT_A_REAL_STATE'));
  });

  test('exception states are reachable from any main-sequence state', () => {
    const client = new OnboardingClient('c1');
    client.transitionTo('AGREEMENT_CONFIRMED');
    client.transitionTo('INTAKE_SENT');
    client.transitionTo('BLOCKED', { reason: 'missing domain access' });
    assert.equal(client.state, 'BLOCKED');
  });

  test('BLOCKED/PAUSED allow re-entry back to the state they left', () => {
    const client = new OnboardingClient('c1');
    client.transitionTo('AGREEMENT_CONFIRMED');
    client.transitionTo('BLOCKED');
    client.transitionTo('AGREEMENT_CONFIRMED'); // re-entry
    assert.equal(client.state, 'AGREEMENT_CONFIRMED');
  });

  test('LAUNCH_APPROVED is gated on the compliance checklist (missing configuration / failed gate)', () => {
    const client = new OnboardingClient('c1');
    for (const state of MAIN_SEQUENCE) {
      if (state === 'PAYMENT_RECEIVED') continue;
      if (state === 'LAUNCH_APPROVED') break;
      client.transitionTo(state);
    }
    assert.equal(client.state, 'CLIENT_REVIEW');
    assert.throws(() => client.transitionTo('LAUNCH_APPROVED'));
    client.markComplianceComplete();
    client.transitionTo('LAUNCH_APPROVED');
    assert.equal(client.state, 'LAUNCH_APPROVED');
  });

  test('CANCELED and OFFBOARDED are terminal', () => {
    const client = new OnboardingClient('c1');
    client.transitionTo('CANCELED');
    assert.throws(() => client.transitionTo('AGREEMENT_CONFIRMED'));
  });

  test('safe offboarding requires the full sequence before archiving', () => {
    const client = new OnboardingClient('c1');
    assert.throws(() => client.offboard({ billingDisabled: true, dataExported: false, accessRevoked: true }));
    client.offboard({ billingDisabled: true, dataExported: true, accessRevoked: true });
    assert.equal(client.state, 'OFFBOARDED');
  });

  test('time-to-launch measures PAYMENT_RECEIVED to LIVE', () => {
    const start = new Date('2026-01-01T00:00:00Z');
    const client = new OnboardingClient('c1', { at: start });
    assert.equal(client.timeToLaunchMs(), null); // not live yet

    let cursor = start;
    for (const state of MAIN_SEQUENCE) {
      if (state === 'PAYMENT_RECEIVED') continue;
      cursor = new Date(cursor.getTime() + 86400000); // +1 day per step
      if (state === 'LAUNCH_APPROVED') client.markComplianceComplete();
      client.transitionTo(state, { at: cursor });
    }
    const ms = client.timeToLaunchMs();
    assert.ok(ms > 0);
    // LIVE is 12 steps after PAYMENT_RECEIVED (excluding PAYMENT_RECEIVED and OPTIMIZATION)
    assert.equal(ms, 12 * 86400000);
  });
});
