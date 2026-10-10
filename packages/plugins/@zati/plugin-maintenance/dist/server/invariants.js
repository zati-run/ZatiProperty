'use strict';
const transitions = Object.freeze({ new: ['quote', 'closed'], quote: ['new', 'progress', 'closed'], progress: ['quote', 'complete'], complete: ['progress', 'closed'], closed: [] });
function deny(code) { const error = new Error(`ZP_MAINTENANCE_${code}`); error.status = 422; throw error; }
const present = value => value !== undefined && value !== null && value !== '';
const sameId = (a, b) => !present(a) && !present(b) || present(a) && present(b) && String(a) === String(b);
function validateContext(values, { property, unit, tenancy }) {
  if (!property || !sameId(property.id, values.propertyId)) deny('PROPERTY_REQUIRED');
  if (present(values.unitId) && (!unit || !sameId(unit.id, values.unitId) || !sameId(unit.propertyId, values.propertyId))) deny('UNIT_CONTEXT');
  if (present(values.tenancyId) && (!tenancy || !present(values.unitId) || !sameId(tenancy.id, values.tenancyId) || !sameId(tenancy.unitId, values.unitId))) deny('TENANCY_CONTEXT');
}
function validExpiry(value, today) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const parsed = new Date(`${value}T00:00:00Z`);
  return !Number.isNaN(parsed.valueOf()) && parsed.toISOString().slice(0, 10) === value && value >= today;
}
function validateVendor(vendor, today) {
  if (!vendor || vendor.active !== true) deny('VENDOR_INACTIVE');
  if (!validExpiry(vendor.insuranceExpiresAt, today)) deny('VENDOR_INSURANCE');
  if (!validExpiry(vendor.licenseExpiresAt, today)) deny('VENDOR_LICENSE');
}
function validateOrder(values, { previous = null, request, vendor, vendorPermission = null, checkLifecycle = true, today = new Date().toISOString().slice(0, 10) }) {
  if (!request || !sameId(request.id, values.requestId)) deny('REQUEST_REQUIRED');
  for (const key of ['propertyId', 'unitId', 'tenancyId']) if (!sameId(values[key], request[key])) deny('REQUEST_CONTEXT');
  if (!Object.hasOwn(transitions, values.state)) deny('STATE_INVALID');
  if (checkLifecycle && !previous && values.state !== 'new') deny('INITIAL_STATE');
  if (previous) {
    for (const key of ['requestId', 'propertyId', 'unitId', 'tenancyId']) if (!sameId(values[key], previous[key])) deny('CONTEXT_IMMUTABLE');
    if (values.state !== previous.state && !transitions[previous.state]?.includes(values.state)) deny('STATE_TRANSITION');
  }
  if (values.approvalRequired !== true || values.approvalGranted !== false) deny('APPROVAL_PROTECTED');
  if (values.state === 'progress' || values.state === 'complete') deny('OWNER_APPROVAL_UNAVAILABLE');
  if (previous?.state === 'complete' && values.state === 'closed') deny('PAYMENT_PROOF_UNAVAILABLE');
  if (checkLifecycle && previous?.state === 'closed') deny('CLOSED_IMMUTABLE');
  if (present(values.vendorId)) {
    validateVendor(vendor, today);
    if (!vendorPermission || !sameId(vendorPermission.vendorId, values.vendorId) || !sameId(vendorPermission.propertyId, values.propertyId)) deny('VENDOR_PROPERTY_PERMISSION');
  }
  if (present(values.estimatedAmount)) {
    const amount = values.estimatedAmount;
    const validNumber = typeof amount === 'number' && Number.isSafeInteger(amount) && amount >= 0;
    const validString = typeof amount === 'string' && /^(0|[1-9][0-9]{0,15})$/.test(amount) && BigInt(amount) <= BigInt(Number.MAX_SAFE_INTEGER);
    if (!validNumber && !validString) deny('ESTIMATE_INVALID');
  }
  if (present(values.currency) && !/^[A-Z]{3}$/.test(values.currency)) deny('CURRENCY_INVALID');
}
module.exports = { deny, present, sameId, validateContext, validateVendor, validateOrder };
