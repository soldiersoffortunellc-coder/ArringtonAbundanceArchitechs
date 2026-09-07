import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { Provisioner, createDryRunAdapter } from '../src/provisioning/dryRunProvisioner.js';

const industryPacks = { insurance: { id: 'insurance' }, 'real-estate': { id: 'real-estate' } };

describe('SaaS provisioning: dry-run, duplicate prevention, tenant isolation, snapshots, global pause, offboarding', () => {
  test('SaaS plan / snapshot selection: rejects an unregistered industry', async () => {
    const provisioner = new Provisioner({ adapter: createDryRunAdapter(), industryPacks });
    await assert.rejects(
      provisioner.provisionSubaccount({ clientId: 'c1', domain: 'a.com', email: 'a@a.com', industry: 'dentistry' }),
    );
  });

  test('subaccount provisioning runs in dry-run mode and logs actions without a live call', async () => {
    const adapter = createDryRunAdapter();
    const provisioner = new Provisioner({ adapter, industryPacks });
    const result = await provisioner.provisionSubaccount({ clientId: 'c1', domain: 'a.com', email: 'a@a.com', industry: 'insurance' });
    assert.equal(result.dryRun, true);
    assert.equal(adapter.actionLog.length, 1);
    assert.equal(adapter.actionLog[0].action, 'createSubaccount');
  });

  test('duplicate account prevention: same domain+email is rejected', async () => {
    const provisioner = new Provisioner({ adapter: createDryRunAdapter(), industryPacks });
    await provisioner.provisionSubaccount({ clientId: 'c1', domain: 'a.com', email: 'a@a.com', industry: 'insurance' });
    await assert.rejects(
      provisioner.provisionSubaccount({ clientId: 'c1-dup', domain: 'a.com', email: 'a@a.com', industry: 'insurance' }),
    );
  });

  test('tenant isolation: two different clients get distinct subaccount ids and independent log entries', async () => {
    const adapter = createDryRunAdapter();
    const provisioner = new Provisioner({ adapter, industryPacks });
    const r1 = await provisioner.provisionSubaccount({ clientId: 'c1', domain: 'a.com', email: 'a@a.com', industry: 'insurance' });
    const r2 = await provisioner.provisionSubaccount({ clientId: 'c2', domain: 'b.com', email: 'b@b.com', industry: 'real-estate' });
    assert.notEqual(r1.subaccountId, r2.subaccountId);
    assert.equal(adapter.actionLog.filter((a) => a.action === 'createSubaccount').length, 2);
  });

  test('industry-pack configuration: applies universal-core before the industry pack', async () => {
    const adapter = createDryRunAdapter();
    const provisioner = new Provisioner({ adapter, industryPacks });
    const result = await provisioner.applySnapshots({ subaccountId: 'sub-1', industry: 'insurance' });
    assert.equal(result.applied, true);
    const layers = adapter.actionLog.filter((a) => a.action === 'applySnapshot').map((a) => a.payload.layer);
    assert.deepEqual(layers, ['universal-core', 'industry-pack:insurance']);
  });

  test('failed snapshot application is handled, not left ambiguous', async () => {
    const adapter = createDryRunAdapter();
    adapter.applySnapshot = async () => {
      throw new Error('simulated snapshot failure');
    };
    const provisioner = new Provisioner({ adapter, industryPacks });
    const result = await provisioner.applySnapshots({ subaccountId: 'sub-1', industry: 'insurance' });
    assert.equal(result.applied, false);
    assert.match(result.reason, /simulated snapshot failure/);
  });

  test('missing configuration is detected before CONFIGURATION completes', () => {
    const provisioner = new Provisioner({ adapter: createDryRunAdapter(), industryPacks });
    const result = provisioner.validateClientConfiguration({ branding: 'x', domain: 'a.com' });
    assert.equal(result.valid, false);
    assert.ok(result.missing.includes('phoneNumber'));
  });

  test('global pause halts all provisioning across every tenant', async () => {
    const provisioner = new Provisioner({ adapter: createDryRunAdapter(), industryPacks });
    provisioner.pauseAll('compliance issue under review');
    await assert.rejects(
      provisioner.provisionSubaccount({ clientId: 'c1', domain: 'a.com', email: 'a@a.com', industry: 'insurance' }),
    );
    provisioner.resumeAll();
    const result = await provisioner.provisionSubaccount({ clientId: 'c1', domain: 'a.com', email: 'a@a.com', industry: 'insurance' });
    assert.equal(result.dryRun, true);
  });

  test('safe offboarding never deletes data first: sequence starts with disableBilling and ends with archive', async () => {
    const provisioner = new Provisioner({ adapter: createDryRunAdapter(), industryPacks });
    const result = await provisioner.safeOffboard({ subaccountId: 'sub-1' });
    assert.equal(result.steps[0].step, 'disableBilling');
    assert.equal(result.steps.at(-1).step, 'archiveSubaccountReference');
    assert.ok(result.steps.map((s) => s.step).includes('exportClientData'));
  });
});
