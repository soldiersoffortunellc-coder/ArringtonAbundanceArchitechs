import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { ROLES, can, assertCan, canViewRawContactData } from '../src/permissions/roles.js';

describe('role permissions', () => {
  test('owner can do anything', () => {
    assert.equal(can(ROLES.OWNER, 'approve:pricing'), true);
    assert.equal(can(ROLES.OWNER, 'anything_at_all'), true);
  });

  test('a role is confined to its granted permissions', () => {
    assert.equal(can(ROLES.SALES_DIRECTOR, 'view:pipeline'), true);
    assert.equal(can(ROLES.SALES_DIRECTOR, 'approve:pricing'), false);
  });

  test('assertCan throws for a disallowed action', () => {
    assert.throws(() => assertCan(ROLES.SALES_DIRECTOR, 'authorize:live_activation'));
  });

  test('an unknown role has no permissions', () => {
    assert.equal(can('not_a_real_role', 'view:pipeline'), false);
  });

  test('raw contact data is restricted to owner and client-facing directors', () => {
    assert.equal(canViewRawContactData(ROLES.OWNER), true);
    assert.equal(canViewRawContactData(ROLES.ONBOARDING_DIRECTOR), true);
    assert.equal(canViewRawContactData(ROLES.SUCCESS_DIRECTOR), true);
    assert.equal(canViewRawContactData(ROLES.REV_OPS_ANALYST), false);
  });
});
