// Client onboarding state machine — matches config/onboarding/state-machine.json
// and docs/12-client-onboarding-system.md exactly.

export const MAIN_SEQUENCE = [
  'PAYMENT_RECEIVED',
  'AGREEMENT_CONFIRMED',
  'INTAKE_SENT',
  'INTAKE_COMPLETED',
  'CREDENTIALS_PENDING',
  'SNAPSHOT_SELECTED',
  'SUBACCOUNT_CREATED',
  'SNAPSHOT_APPLIED',
  'CONFIGURATION',
  'INTEGRATION_TESTING',
  'CLIENT_REVIEW',
  'LAUNCH_APPROVED',
  'LIVE',
  'OPTIMIZATION',
];

export const EXCEPTION_STATES = ['BLOCKED', 'PAUSED', 'CANCELED', 'REFUND_REVIEW', 'OFFBOARDED'];
export const TERMINAL_STATES = ['CANCELED', 'OFFBOARDED'];

export class OnboardingClient {
  constructor(clientId, { at = new Date() } = {}) {
    this.clientId = clientId;
    this.state = 'PAYMENT_RECEIVED';
    this.history = [{ from: null, to: 'PAYMENT_RECEIVED', at }];
    this.preExceptionState = null;
    this.complianceChecklistComplete = false;
  }

  markComplianceComplete() {
    this.complianceChecklistComplete = true;
  }

  transitionTo(nextState, { at = new Date(), reason } = {}) {
    if (TERMINAL_STATES.includes(this.state)) {
      throw new Error(`Cannot transition: "${this.state}" is terminal`);
    }

    const isMainForward =
      MAIN_SEQUENCE.includes(this.state) &&
      MAIN_SEQUENCE.includes(nextState) &&
      MAIN_SEQUENCE.indexOf(nextState) === MAIN_SEQUENCE.indexOf(this.state) + 1;

    const isToException = EXCEPTION_STATES.includes(nextState);

    const isReentryFromException =
      EXCEPTION_STATES.includes(this.state) &&
      !TERMINAL_STATES.includes(this.state) &&
      nextState === this.preExceptionState;

    if (!isMainForward && !isToException && !isReentryFromException) {
      throw new Error(`Illegal transition from "${this.state}" to "${nextState}"`);
    }

    if (nextState === 'LAUNCH_APPROVED' && !this.complianceChecklistComplete) {
      throw new Error('Cannot reach LAUNCH_APPROVED: compliance checklist is not complete');
    }

    if (isToException && !EXCEPTION_STATES.includes(this.state)) {
      this.preExceptionState = this.state;
    }

    this.history.push({ from: this.state, to: nextState, at, reason });
    this.state = nextState;
    return this;
  }

  /** Safe offboarding: disable billing -> export data -> revoke access -> archive. Never deletes data first. */
  offboard({ billingDisabled, dataExported, accessRevoked, at = new Date() }) {
    if (!billingDisabled || !dataExported || !accessRevoked) {
      throw new Error('Safe offboarding requires billingDisabled, dataExported, and accessRevoked to all be true before archiving');
    }
    return this.transitionTo('OFFBOARDED', { at, reason: 'safe-offboard-sequence-complete' });
  }

  /** Milliseconds from PAYMENT_RECEIVED to LIVE, or null if not yet LIVE. */
  timeToLaunchMs() {
    const paymentEvent = this.history.find((h) => h.to === 'PAYMENT_RECEIVED');
    const liveEvent = this.history.find((h) => h.to === 'LIVE');
    if (!paymentEvent || !liveEvent) return null;
    return liveEvent.at.getTime() - paymentEvent.at.getTime();
  }
}
