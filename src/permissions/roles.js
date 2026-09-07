// Role-based permission checks for the Executive Command Center and agent
// file-ownership boundaries. Per docs/10-revenue-agent-definitions.md and
// docs/15-executive-command-center-spec.md "Access" section.

export const ROLES = Object.freeze({
  OWNER: 'owner',
  CRO: 'chief_revenue_officer',
  MARKET_ANALYST: 'market_opportunity_analyst',
  PRODUCTIZATION_DIRECTOR: 'productization_director',
  SALES_DIRECTOR: 'sales_director',
  ONBOARDING_DIRECTOR: 'client_onboarding_director',
  SUCCESS_DIRECTOR: 'client_success_retention_director',
  REV_OPS_ANALYST: 'revenue_operations_analyst',
});

const PERMISSIONS = {
  [ROLES.OWNER]: ['*'],
  [ROLES.CRO]: [
    'view:full_rollup', 'approve:pricing', 'approve:vertical_activation', 'authorize:live_activation',
  ],
  [ROLES.MARKET_ANALYST]: ['edit:scorecard'],
  [ROLES.PRODUCTIZATION_DIRECTOR]: ['edit:snapshots'],
  [ROLES.SALES_DIRECTOR]: ['view:pipeline', 'view:close_rate', 'edit:pipeline'],
  [ROLES.ONBOARDING_DIRECTOR]: [
    'view:implementation_capacity', 'view:time_to_launch', 'edit:onboarding_state', 'approve:launch',
  ],
  [ROLES.SUCCESS_DIRECTOR]: [
    'view:client_health', 'view:churn_risk', 'edit:interventions', 'approve:testimonial_use',
  ],
  [ROLES.REV_OPS_ANALYST]: ['view:full_rollup', 'edit:revenue_ledger'],
};

export function can(role, permission) {
  const granted = PERMISSIONS[role];
  if (!granted) return false;
  return granted.includes('*') || granted.includes(permission);
}

export function assertCan(role, permission) {
  if (!can(role, permission)) {
    throw new Error(`Role "${role}" is not permitted to "${permission}"`);
  }
}

/** No role except the owner and the client's own directors see raw cross-client contact data via rollup views. */
export function canViewRawContactData(role) {
  return role === ROLES.OWNER || role === ROLES.ONBOARDING_DIRECTOR || role === ROLES.SUCCESS_DIRECTOR;
}
