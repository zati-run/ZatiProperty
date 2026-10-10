'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const invariants = require('../dist/server/invariants');
const source = fs.readFileSync(require.resolve('../dist/server/index'), 'utf8');
const mod = { exports: {} };
vm.runInNewContext('(function(require,module,exports){' + source + '\n})', {})(name => name === '@nocobase/server' ? { Plugin: class {} } : invariants, mod, mod.exports);
const Plugin = mod.exports;
const tx = { LOCK: { UPDATE: 'UPDATE' } };
const records = () => ({ zp_properties: { 1: { id: 1 }, 9: { id: 9 } }, zp_units: { 2: { id: 2, propertyId: 1 } }, zp_tenancies: { 3: { id: 3, unitId: 2 } }, zp_maintenance_requests: { 4: { id: 4, propertyId: 1, unitId: 2, tenancyId: 3 } }, zp_vendors: { 5: { id: 5, active: true, insuranceExpiresAt: '2099-01-01', licenseExpiresAt: '2099-01-01' } }, zp_vendor_properties: { 7: { id: 7, vendorId: 5, propertyId: 1 } }, zp_work_orders: {} });
const order = () => ({ id: 6, requestId: 4, propertyId: 1, unitId: 2, tenancyId: 3, vendorId: 5, state: 'new', approvalRequired: true, approvalGranted: false });
function instance(name, values, isNewRecord = true, previous = values) { return { constructor: { name }, isNewRecord, get: key => typeof key === 'string' ? values[key] : { ...values }, set: (key, value) => { values[key] = value; }, previous: key => previous[key] }; }
async function setup() {
  const hooks = new Map(), rows = records(), reads = [];
  const plugin = new Plugin();
  plugin.db = { on: (name, fn) => hooks.set(name, fn), getModel: name => ({ findOne: async options => { reads.push(options); const row = Object.values(rows[name] || {}).find(row => Object.entries(options.where).every(([key, value]) => String(row[key]) === String(value))); return row ? instance(name, row) : null; } }) };
  await plugin.load();
  return { hooks, rows, reads };
}
test('native hook adapter requires transaction and locks context reads', async () => {
  const { hooks, reads } = await setup();
  const hook = hooks.get('zp_work_orders.beforeSave');
  await assert.rejects(hook(instance('zp_work_orders', order()), {}), /TRANSACTION_REQUIRED/);
  await hook(instance('zp_work_orders', order()), { transaction: tx });
  assert.ok(reads.length >= 5);
  assert.ok(reads.every(read => read.transaction === tx && read.lock === 'UPDATE'));
});
test('missing request/property and cross-context links fail in persistence hook', async () => {
  const { hooks } = await setup(); const hook = hooks.get('zp_work_orders.beforeSave');
  for (const change of [{ requestId: null }, { propertyId: null }, { unitId: 99 }, { tenancyId: 99 }, { propertyId: 9 }, { approvalGranted: true }]) await assert.rejects(hook(instance('zp_work_orders', { ...order(), ...change }), { transaction: tx }));
});
test('stale updates and association-setter foreign key changes cannot bypass context protection', async () => {
  const { hooks, rows } = await setup(); const hook = hooks.get('zp_work_orders.beforeSave');
  const previous = order(); rows.zp_work_orders[6] = previous;
  await hook(instance('zp_work_orders', { ...previous, state: 'quote' }, false, previous), { transaction: tx });
  await assert.rejects(hook(instance('zp_work_orders', { ...previous, propertyId: 9 }, false, previous), { transaction: tx }), /CONTEXT_IMMUTABLE/);
  rows.zp_work_orders[6] = { ...previous, state: 'quote' };
  await assert.rejects(hook(instance('zp_work_orders', previous, false, previous), { transaction: tx }), /STALE_UPDATE/);
});
test('parent hierarchy updates, bulk writes and deletes are guarded', async () => {
  const { hooks } = await setup();
  await assert.rejects(hooks.get('zp_units.beforeUpdate')(instance('zp_units', { id: 2, propertyId: 9 }, false), { transaction: tx }), /HIERARCHY_IMMUTABLE/);
  await assert.rejects(hooks.get('zp_tenancies.beforeUpdate')(instance('zp_tenancies', { id: 3, unitId: 9 }, false), { transaction: tx }), /HIERARCHY_IMMUTABLE/);
  for (const name of ['zp_work_orders.beforeBulkUpdate', 'zp_work_orders.beforeDestroy', 'zp_units.beforeBulkUpdate', 'zp_properties.beforeDestroy']) assert.throws(() => hooks.get(name)());
});
test('post-association validation catches foreign key mismatch before transaction commits', async () => {
  const { hooks } = await setup();
  await assert.rejects(hooks.get('zp_work_orders.afterSaveWithAssociations')(instance('zp_work_orders', { ...order(), tenancyId: 99 }, false), { transaction: tx }), /TENANCY_CONTEXT/);
});

test('native hook checks property permission in transaction, rejecting eligible unmapped vendor', async () => {
  const { hooks, rows, reads } = await setup();
  rows.zp_vendor_properties = {};
  await assert.rejects(hooks.get('zp_work_orders.beforeSave')(instance('zp_work_orders', order()), { transaction: tx }), /VENDOR_PROPERTY_PERMISSION/);
  const permissionRead = reads.find(read => read.where.vendorId === 5 && read.where.propertyId === 1);
  assert.ok(permissionRead);
  assert.equal(permissionRead.transaction, tx);
  assert.equal(permissionRead.lock, 'UPDATE');
});

test('dist-only plugin declares inspected runtime dependency for native compatibility check', () => {
  const versions = require('../dist/externalVersion');
  const manifest = require('../package.json');
  assert.deepEqual(versions, { '@nocobase/server': '2.2.21', '@nocobase/client': '2.2.21' });
  assert.equal(manifest.peerDependencies['@nocobase/client'], versions['@nocobase/client']);
  assert.equal(manifest.peerDependencies['@nocobase/server'], versions['@nocobase/server']);
  assert.ok(manifest.files.includes('dist'));
});
