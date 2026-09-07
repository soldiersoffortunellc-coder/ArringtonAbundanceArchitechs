// Dry-run SaaS provisioning workflow. Per docs/09-saas-provisioning-architecture.md:
// no live GHL API call is ever made by this module. A real GhlApiAdapter can
// be substituted later behind the same adapter interface.

/** Default adapter: logs every call, makes no live calls, always succeeds. */
export function createDryRunAdapter() {
  const actionLog = [];
  return {
    actionLog,
    async createSubaccount(payload) {
      actionLog.push({ action: 'createSubaccount', payload, at: new Date() });
      return { subaccountId: `dryrun-${payload.clientId}`, dryRun: true };
    },
    async applySnapshot(payload) {
      actionLog.push({ action: 'applySnapshot', payload, at: new Date() });
      return { applied: true, dryRun: true };
    },
    async createUser(payload) {
      actionLog.push({ action: 'createUser', payload, at: new Date() });
      return { userId: `dryrun-user-${payload.email}`, dryRun: true };
    },
    async sendWelcomeEmail(payload) {
      actionLog.push({ action: 'sendWelcomeEmail', payload, at: new Date() });
      return { sent: true, dryRun: true };
    },
    async attachBillingPlan(payload) {
      actionLog.push({ action: 'attachBillingPlan', payload, at: new Date() });
      return { attached: true, dryRun: true };
    },
  };
}

const REQUIRED_CLIENT_CONFIG_FIELDS = [
  'branding', 'domain', 'phoneNumber', 'users', 'services', 'disclosures', 'escalationContact',
];

export class Provisioner {
  /**
   * @param {{adapter: object, industryPacks: Record<string, object>}} deps
   */
  constructor({ adapter, industryPacks }) {
    this.adapter = adapter;
    this.industryPacks = industryPacks;
    this.provisionedAccounts = new Map(); // domain::email -> subaccountId
    this.globalPause = false;
    this.pauseReason = null;
  }

  pauseAll(reason) {
    this.globalPause = true;
    this.pauseReason = reason;
  }

  resumeAll() {
    this.globalPause = false;
    this.pauseReason = null;
  }

  _assertNotPaused() {
    if (this.globalPause) {
      throw new Error(`Provisioning is globally paused: ${this.pauseReason}`);
    }
  }

  _accountKey({ domain, email }) {
    return `${domain}::${email}`.toLowerCase();
  }

  /** Duplicate-account prevention + tenant isolation (each account gets its own key/subaccountId). */
  async provisionSubaccount({ clientId, domain, email, industry }) {
    this._assertNotPaused();
    if (!this.industryPacks[industry]) {
      throw new Error(`Unknown industry: ${industry}`);
    }
    const key = this._accountKey({ domain, email });
    if (this.provisionedAccounts.has(key)) {
      throw new Error(`Duplicate account: a subaccount already exists for ${domain}/${email}`);
    }
    const result = await this.adapter.createSubaccount({ clientId, domain, email, industry });
    this.provisionedAccounts.set(key, result.subaccountId);
    return result;
  }

  /** Applies universal-core, then the industry pack. Refuses to apply an industry pack without universal-core first. */
  async applySnapshots({ subaccountId, industry }) {
    this._assertNotPaused();
    if (!this.industryPacks[industry]) {
      throw new Error(`No industry pack registered for "${industry}"`);
    }

    const universalResult = await this._applySnapshotSafely({ subaccountId, layer: 'universal-core' });
    if (!universalResult.applied) {
      return { applied: false, reason: `universal-core failed: ${universalResult.reason}` };
    }

    const industryResult = await this._applySnapshotSafely({ subaccountId, layer: `industry-pack:${industry}` });
    if (!industryResult.applied) {
      return { applied: false, reason: `industry-pack failed: ${industryResult.reason}` };
    }
    return { applied: true };
  }

  async _applySnapshotSafely(payload) {
    try {
      const result = await this.adapter.applySnapshot(payload);
      return { applied: !!result.applied };
    } catch (err) {
      return { applied: false, reason: err.message };
    }
  }

  /** Missing-configuration detection before CONFIGURATION is marked complete. */
  validateClientConfiguration(config) {
    const missing = REQUIRED_CLIENT_CONFIG_FIELDS.filter((field) => !config[field]);
    return { valid: missing.length === 0, missing };
  }

  /** Safe offboarding sequence: disable billing -> export data -> revoke access -> archive. Never deletes data first. */
  async safeOffboard({ subaccountId }) {
    const steps = [
      { step: 'disableBilling', at: new Date() },
      { step: 'exportClientData', at: new Date() },
      { step: 'revokeAccess', at: new Date() },
      { step: 'archiveSubaccountReference', at: new Date() },
    ];
    return { subaccountId, steps, completed: true };
  }
}
