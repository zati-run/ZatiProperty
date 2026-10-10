'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { validateContext, validateVendor, validateOrder } = require('../dist/server/invariants');
const today = '2026-10-11';
const request = { id: 4, propertyId: 1, unitId: 2, tenancyId: 3 };
const vendor = { id: 5, active: true, insuranceExpiresAt: '2027-01-01', licenseExpiresAt: '2027-01-01' };
const order = { ...request, id: 6, requestId: 4, vendorId: 5, state: 'new', approvalRequired: true, approvalGranted: false, estimatedAmount: 25000, currency: 'USD' };
const context = { property: { id: 1 }, unit: { id: 2, propertyId: 1 }, tenancy: { id: 3, unitId: 2 } };
const check = (value, previous = null, extras = {}) => validateOrder(value, { previous, request, vendor, vendorPermission: { vendorId: 5, propertyId: 1 }, today, ...extras });
test('allows consistent property, unit and tenancy; rejects each cross-context link', () => {
  validateContext(request, context);
  for (const [key, value] of [['propertyId', 9], ['unitId', 9], ['tenancyId', 9], ['unitId', null]]) assert.throws(() => validateContext({ ...request, [key]: value }, context));
  validateContext({ propertyId: 1 }, { property: { id: 1 } });
});
test('vendor must be active with valid unexpired insurance and license', () => {
  validateVendor(vendor, today);
  validateVendor({ ...vendor, insuranceExpiresAt: today }, today);
  for (const change of [{ active: false }, { insuranceExpiresAt: null }, { insuranceExpiresAt: '2026-10-10' }, { licenseExpiresAt: '2026-02-31' }, { licenseExpiresAt: '2026-10-10' }]) assert.throws(() => validateVendor({ ...vendor, ...change }, today));
});
test('new order may assign a permitted vendor and transition to quote', () => {
  check(order);
  check({ ...order, state: 'quote' }, order);
  check({ ...order, vendorId: null }, order, { vendor: null });
});
test('blocks forged approvals and financial progression', () => {
  for (const change of [{ approvalRequired: false }, { approvalGranted: true }, { state: 'progress' }, { state: 'complete' }]) assert.throws(() => check({ ...order, ...change }, { ...order, state: 'quote' }));
  assert.throws(() => check({ ...order, state: 'closed' }, { ...order, state: 'complete' }), /PAYMENT_PROOF_UNAVAILABLE/);
});
test('requires New creation and valid directed lifecycle; closed records immutable', () => {
  assert.throws(() => check({ ...order, state: 'quote' }), /INITIAL_STATE/);
  check({ ...order, state: 'new' }, { ...order, state: 'quote' });
  check({ ...order, state: 'quote' }, { ...order, state: 'progress' });
  assert.throws(() => check({ ...order, state: 'new' }, { ...order, state: 'progress' }), /STATE_TRANSITION/);
  assert.throws(() => check({ ...order, state: 'progress' }, { ...order, state: 'complete' }), { code: 'ZP_MAINTENANCE_OWNER_APPROVAL_UNAVAILABLE', message: /Owner approval is required.*No changes were saved/ });
  check({ ...order, state: 'closed' }, order);
  check({ ...order, state: 'closed' }, { ...order, state: 'quote' });
  assert.throws(() => check({ ...order, state: 'closed' }, { ...order, state: 'closed' }), /CLOSED_IMMUTABLE/);
  assert.throws(() => check({ ...order, state: 'bad' }), /STATE_INVALID/);
});
test('rejects altered request or property context and invalid money representation', () => {
  for (const change of [{ requestId: 10 }, { propertyId: 9 }, { unitId: 9 }, { tenancyId: 9 }, { estimatedAmount: -1 }, { estimatedAmount: 1.1 }, { estimatedAmount: Number.MAX_SAFE_INTEGER + 1 }, { currency: 'usd' }]) assert.throws(() => check({ ...order, ...change }, order));
});

test('active insured vendor still requires explicit permission for this property', () => {
  assert.throws(() => check(order, null, { vendorPermission: null }), /VENDOR_PROPERTY_PERMISSION/);
  assert.throws(() => check(order, null, { vendorPermission: { vendorId: 5, propertyId: 9 } }), /VENDOR_PROPERTY_PERMISSION/);
  assert.throws(() => check(order, null, { vendorPermission: { vendorId: 8, propertyId: 1 } }), /VENDOR_PROPERTY_PERMISSION/);
});

test('persisted bigint strings preserve integer minor amounts without coercion', () => {
  for (const estimatedAmount of ['0', '25000', String(Number.MAX_SAFE_INTEGER), 0, Number.MAX_SAFE_INTEGER]) check({ ...order, estimatedAmount }, order);
  for (const estimatedAmount of ['01', '+1', '-1', '1.0', '1e3', ' 1', '1 ', '9007199254740992', '999999999999999999999999', true, {}, 1.5]) assert.throws(() => check({ ...order, estimatedAmount }, order), /ESTIMATE_INVALID/);
});
